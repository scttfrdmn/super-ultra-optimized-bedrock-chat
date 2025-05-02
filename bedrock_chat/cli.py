#!/usr/bin/env python3
import json, os, boto3, typer
from rich import console, live, markdown, table
from .__version__ import __version__

app, con = typer.Typer(rich_markup_mode="rich"), console.Console()

def get_test_payload(mid): return json.dumps({"inputText": "."} if "anthropic" not in mid else {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1, "messages": [{"role": "user", "content": [{"type": "text", "text": "."}]}]})

def init_chat(region="us-east-1", profile=None):
    session, models, access, enabled = boto3.Session(profile_name=profile) if profile else boto3.Session(), {}, {}, set()
    rt, bdr = session.client("bedrock-runtime", region_name=region), session.client("bedrock", region_name=region)
    for m in bdr.list_foundation_models().get("modelSummaries", []):
        if "TEXT" not in [mode.upper() for mode in m.get("outputModalities", [])]: continue
        mid, alias = m["modelId"], m["modelId"].split(".")[-1].split("-v")[0]
        models[alias], access[alias] = mid, ("On-Demand" if "ON_DEMAND" in m.get("inferenceTypesSupported", []) else "InferenceProfile" if "INFERENCE_PROFILE" in m.get("inferenceTypesSupported", []) else "Provisioned")
        try: rt.invoke_model(modelId=mid, body=get_test_payload(mid)); enabled.add(alias)
        except: pass
    try:
        for p in bdr.list_inference_profiles().get("inferenceProfileSummaries", []):
            alias, pid = p.get("inferenceProfileId", "").split(".")[-1], p.get("inferenceProfileId", "")
            models[alias], access[alias] = pid, "InferenceProfile"
            try: rt.invoke_model(modelId=pid, body=get_test_payload(pid)); enabled.add(alias)
            except: pass
    except: pass
    return rt, models, access, enabled

def stream_chat(rt, model, msg, history=[]):
    body = {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024, "messages": history + [{"role": "user", "content": [{"type": "text", "text": msg}]}]} if "anthropic" in model else {"inputText": msg, "textGenerationConfig": {"maxTokenCount": 512}}
    txt = ""
    with live.Live(markdown.Markdown("")) as l:
        for c in rt.invoke_model_with_response_stream(modelId=model, body=json.dumps(body)).get("body"):
            if "chunk" in c:
                data = json.loads(c["chunk"]["bytes"])
                txt += (data.get("delta", {}).get("text", "") if "anthropic" in model and "delta" in data else "".join([b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]) if "anthropic" in model else data.get("completion", "")); l.update(markdown.Markdown(txt))
    return txt, (history + [{"role": "user", "content": [{"type": "text", "text": msg}]}, {"role": "assistant", "content": [{"type": "text", "text": txt}]}]) if txt.strip() else history

@app.callback(invoke_without_command=True)
def main(version: bool = typer.Option(False, "--version", "-v"), profile: str = typer.Option(None, "--profile"), region: str = typer.Option("us-east-1", "--region"), ctx: typer.Context = typer.Context):
    if version: con.print(f"ultra-optimized-bedrock-chat v{__version__}"); raise typer.Exit()
    globals()["profile"], globals()["region"] = profile, region
    if ctx.invoked_subcommand is None: start_chat()

@app.command()
def start_chat(clear: bool = False, all: bool = False):
    if clear: os.system("cls" if os.name == "nt" else "clear")
    with con.status("Loading..."): rt, models, access, enabled = init_chat(globals().get("region", "us-east-1"), globals().get("profile"))
    tbl = table.Table(title=f"ultra-optimized-bedrock-chat v{__version__} - Models")
    [tbl.add_column(c, s) for c,s in [("Alias", "cyan"), ("ID", "green"), ("Access", "yellow")]]
    [tbl.add_row(a, i[:40]+"..." if len(i)>40 else i, access.get(a,"")) for a,i in sorted(models.items(), key=lambda x: (x[0] not in enabled, access.get(x[0],""), x[0])) if all or a in enabled]
    con.print(tbl); history = []; choice = typer.prompt("Model")
    model = choice.split(":")[0] if ":" in choice and not choice.startswith(("arn:", "us.")) else choice if choice.startswith(("arn:", "us.")) else models.get(choice, choice)
    if not model: con.print("Model not found!"); return
    con.print(f"Using {model} (exit/clear)")
    while (msg := typer.prompt("", prompt_suffix="You: ")) != "exit":
        if msg == "clear": history = []; con.print("History cleared"); continue
        try: con.print("AI:", end=" "); response, history = stream_chat(rt, model, msg, history); con.print() if response.strip() else con.print("No response")
        except Exception as e: con.print(f"Error: {e}")

if __name__ == "__main__": app()