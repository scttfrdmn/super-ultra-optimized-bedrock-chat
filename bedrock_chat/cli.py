#!/usr/bin/env python3
"""AWS Bedrock ChatBot - Extreme optimization (<50 lines)"""
import json, os, boto3, typer
from rich import console, live, markdown, table

app, con = typer.Typer(), console.Console()

class Chat:
    def __init__(self, region="us-east-1"):
        self.rt = boto3.client("bedrock-runtime", region_name=region)
        self.bdr = boto3.client("bedrock", region_name=region)
        # Get foundation + provisioned models
        self.models = {m["modelId"].split(".")[-1].split("-v")[0]: m["modelId"] 
                for m in self.bdr.list_foundation_models().get("modelSummaries", [])
                if "text" in m.get("outputModalities", [])}
        try:
            self.models.update({f"prov-{m.get('provisionedModelName', '')}": m.get('provisionedModelArn', "")
                for m in self.bdr.list_provisioned_model_throughputs().get("provisionedModelSummaries", [])})
        except: pass  # Skip if no permissions
        self.history, self.model = [], None
    
    def stream(self, msg):
        # Format prompt + invoke stream
        body = {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024,
                "messages": self.history + [{"role": "user", "content": [{"type": "text", "text": msg}]}]} \
               if "anthropic" in self.model else \
               {"inputText": msg, "textGenerationConfig": {"maxTokenCount": 512}}
        resp = self.rt.invoke_model_with_response_stream(modelId=self.model, body=json.dumps(body))
        
        # Process stream
        txt = ""
        with live.Live(markdown.Markdown("")) as live_display:
            for c in resp.get("body"):
                if "chunk" in c:
                    data = json.loads(c["chunk"]["bytes"])
                    token = data["content"][0].get("text", "") if "anthropic" in self.model and "content" in data \
                           and data["content"] else data.get("completion", "")
                    txt += token
                    live_display.update(markdown.Markdown(txt))
        
        # Update history
        self.history.extend([{"role": "user", "content": [{"type": "text", "text": msg}]},
                           {"role": "assistant", "content": [{"type": "text", "text": txt}]}])
        return txt

@app.command()
def chat(region: str = "us-east-1", clear: bool = False):
    """AWS Bedrock chat with foundation & provisioned models"""
    if clear: os.system("cls" if os.name == "nt" else "clear")
    bot = Chat(region)
    
    # Show models & get selection
    tbl = table.Table(title="Models")
    [tbl.add_column(c, style=s) for c, s in [("Alias", "cyan"), ("ID", "green")]]
    [tbl.add_row(a, i[:50] + "..." if len(i) > 50 else i) for a, i in bot.models.items()]
    con.print(tbl)
    
    # Select model & start chat loop
    choice = typer.prompt("Model (name/ID/ARN)")
    bot.model = choice if choice.startswith("arn:") else bot.models.get(choice, choice)
    con.print(f"Using [bold]{bot.model}[/bold] (exit/clear)")
    
    while (msg := typer.prompt("", prompt_suffix="\nYou: ")) != "exit":
        if msg == "clear": bot.history = []; con.print("[italic]History cleared[/italic]"); continue
        try: con.print("AI:"); bot.stream(msg); con.print()
        except Exception as e: con.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__": app()