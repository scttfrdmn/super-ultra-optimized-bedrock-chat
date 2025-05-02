#!/usr/bin/env python3
"""AWS Bedrock chat (<50 lines) with enabled model detection"""
import json, os, boto3, typer
from rich import console, live, markdown, table
from .__version__ import __version__
app, con = typer.Typer(rich_markup_mode="rich"), console.Console()
app.state = type('obj', (object,), {})  # Create a simple state object

class Chat:
    def __init__(self, region="us-east-1", profile=None):
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.rt, self.bdr = session.client("bedrock-runtime", region_name=region), session.client("bedrock", region_name=region)
        self.models, self.access, enabled = {}, {}, set()
        # Load foundation models with access types
        for m in self.bdr.list_foundation_models().get("modelSummaries", []):
            if "TEXT" not in [mode.upper() for mode in m.get("outputModalities", [])]: continue
            mid, alias = m["modelId"], m["modelId"].split(".")[-1].split("-v")[0]
            self.models[alias], self.access[alias] = mid, ("On-Demand" if "ON_DEMAND" in m.get("inferenceTypesSupported", []) 
                else "InferenceProfile" if "INFERENCE_PROFILE" in m.get("inferenceTypesSupported", []) else "Provisioned")
            try: # Test if model is enabled
                if self.access[alias] == "On-Demand": self.rt.invoke_model(modelId=mid, 
                    body=json.dumps({"inputText": "."} if "anthropic" not in mid else 
                    {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1, 
                    "messages": [{"role": "user", "content": [{"type": "text", "text": "."}]}]})); enabled.add(alias)
            except: pass
        # Add inference profiles
        try:
            for p in self.bdr.list_inference_profiles().get("inferenceProfileSummaries", []):
                alias, pid = p.get("inferenceProfileId", "").split(".")[-1], p.get("inferenceProfileId", "")
                self.models[alias], self.access[alias] = pid, "InferenceProfile"
                try: self.rt.invoke_model(modelId=pid, body=json.dumps({"inputText": "."} if "anthropic" not in pid else 
                     {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1, 
                     "messages": [{"role": "user", "content": [{"type": "text", "text": "."}]}]})); enabled.add(alias)
                except: pass
        except: pass
        self.enabled, self.history, self.model = enabled, [], None
    
    def stream(self, msg):
        body = {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024, "messages": 
               self.history + [{"role": "user", "content": [{"type": "text", "text": msg}]}]} if "anthropic" in self.model else \
               {"inputText": msg, "textGenerationConfig": {"maxTokenCount": 512}}
        resp = self.rt.invoke_model_with_response_stream(modelId=self.model, body=json.dumps(body)); txt = ""
        with live.Live(markdown.Markdown("")) as l:
            for c in resp.get("body"):
                if "chunk" in c:
                    data = json.loads(c["chunk"]["bytes"])
                    if "anthropic" in self.model:
                        # Handle Claude model response format
                        if "delta" in data and "text" in data["delta"]:
                            # Handle new Claude streaming format
                            token = data["delta"]["text"]
                            txt += token
                        elif "content" in data and data["content"] and len(data["content"]) > 0:
                            # Handle older response format
                            for content_block in data["content"]:
                                if content_block.get("type") == "text":
                                    token = content_block.get("text", "")
                                    txt += token
                    else:
                        # Handle non-Claude model response
                        token = data.get("completion", "")
                        txt += token
                    l.update(markdown.Markdown(txt))
        # Only add to history if we got a non-empty response
        if txt.strip():
            self.history.append({"role": "user", "content": [{"type": "text", "text": msg}]})
            self.history.append({"role": "assistant", "content": [{"type": "text", "text": txt}]})
        return txt

@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show the application version and exit."),
    profile: str = typer.Option(None, "--profile", help="AWS profile name to use"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region to use"),
    ctx: typer.Context = typer.Context,
):
    """AWS Bedrock chat with automatic model availability detection"""
    if version:
        con.print(f"ultra-optimized-bedrock-chat version: {__version__}")
        raise typer.Exit()
    
    # Store profile and region at app level for commands to access
    app.state.profile = profile
    app.state.region = region
    
    # If no subcommand is provided, automatically run chat subcommand
    if ctx.invoked_subcommand is None:
        chat()

@app.command()
def chat(clear: bool = False, all: bool = False):
    """Start the Bedrock chat interface"""
    if clear: os.system("cls" if os.name == "nt" else "clear")
    with con.status("[italic]Determining enabled models, please wait...[/italic]") as status:
        # Use profile and region from app state
        region = app.state.region
        profile = app.state.profile
        bot = Chat(region, profile)
        tbl = table.Table(title=f"ultra-optimized-bedrock-chat v{__version__} - Models")
        [tbl.add_column(c, style=s) for c,s in [("Alias", "cyan"), ("ID", "green"), ("Access", "yellow")]]
        for a, i in sorted(bot.models.items(), key=lambda x: (x[0] not in bot.enabled, bot.access.get(x[0], ""), x[0])):
            if all or a in bot.enabled: tbl.add_row(a, i[:40]+"..." if len(i)>40 else i, bot.access.get(a,""))
        status.stop()
    con.print(tbl); choice = typer.prompt("Model (Alias/ID/ARN)")
    bot.model = choice if choice.startswith("arn:") or choice.startswith("us.") else bot.models.get(choice, choice)
    # Remove version suffix with colon if present (e.g., model-name:0)
    if ":" in bot.model and not bot.model.startswith("arn:") and not bot.model.startswith("us."):
        bot.model = bot.model.split(":")[0]
    if not bot.model: con.print("[bold red]Model not found![/bold red]"); return
    con.print(f"Using [bold]{bot.model}[/bold] (exit/clear)")
    while (msg := typer.prompt("", prompt_suffix="\nYou: ")) != "exit":
        if msg == "clear": bot.history = []; con.print("[italic]History cleared[/italic]"); continue
        try: 
            con.print("AI:", end=" ")
            response = bot.stream(msg)
            # Ensure we print the response properly
            if not response.strip():
                con.print("[italic]No response received[/italic]")
            con.print()
        except Exception as e: con.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__": app()