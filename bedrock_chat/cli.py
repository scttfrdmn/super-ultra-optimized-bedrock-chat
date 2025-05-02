#!/usr/bin/env python3
import json, os, boto3, typer
from rich import console, live, markdown, table
from .__version__ import __version__

app, con = typer.Typer(rich_markup_mode="rich"), console.Console()

def init_models(region="us-east-1", profile=None):
    s = boto3.Session(profile_name=profile) if profile else boto3.Session()
    rt, bd, ms, en = s.client("bedrock-runtime", region_name=region), s.client("bedrock", region_name=region), {}, set()
    test = lambda m: json.dumps({"inputText": "."} if "anthropic" not in m else {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1, "messages": [{"role": "user", "content": [{"type": "text", "text": "."}]}]})
    for m in bd.list_foundation_models().get("modelSummaries", []):
        if "TEXT" in [mode.upper() for mode in m.get("outputModalities", [])]:
            mid, a = m["modelId"], m["modelId"].split(".")[-1].split("-v")[0]; ms[a] = mid
            try: rt.invoke_model(modelId=mid, body=test(mid)); en.add(a)
            except: pass
    try: 
        for p in bd.list_inference_profiles().get("inferenceProfileSummaries", []):
            a, pid = p.get("inferenceProfileId", "").split(".")[-1], p.get("inferenceProfileId", ""); ms[a] = pid
            try: rt.invoke_model(modelId=pid, body=test(pid)); en.add(a)
            except: pass
    except: pass
    return rt, ms, en

def chat(rt, model, msg, hist=None):
    hist, txt, ic = hist or [], "", "anthropic" in model
    body = json.dumps({"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024, "messages": hist + [{"role": "user", "content": [{"type": "text", "text": msg}]}]} if ic else {"inputText": msg, "textGenerationConfig": {"maxTokenCount": 512}})
    with live.Live(markdown.Markdown("")) as l:
        for c in rt.invoke_model_with_response_stream(modelId=model, body=body).get("body"):
            if "chunk" in c:
                d = json.loads(c["chunk"]["bytes"])
                token = (d.get("delta", {}).get("text", "") if "delta" in d else "".join([b.get("text", "") for b in d.get("content", []) if b.get("type") == "text"])) if ic else d.get("completion", "")
                txt += token; l.update(markdown.Markdown(txt))
    return txt, (hist + [{"role": "user", "content": [{"type": "text", "text": msg}]}, {"role": "assistant", "content": [{"type": "text", "text": txt}]}]) if txt.strip() else hist

@app.callback(invoke_without_command=True)
def main(v: bool = typer.Option(False, "--version", "-v"), p: str = typer.Option(None, "--profile"), r: str = typer.Option("us-east-1", "--region"), c: typer.Context = typer.Context):
    if v: con.print(f"ultra-optimized-bedrock-chat v{__version__}"); raise typer.Exit()
    globals().update({"profile": p, "region": r}); c.invoked_subcommand or start_chat()

@app.command()
def start_chat(clear: bool = False, all: bool = False):
    if clear: os.system("cls" if os.name == "nt" else "clear")
    with con.status("Loading..."): rt, ms, en = init_models(globals().get("region"), globals().get("profile"))
    t = table.Table()
    for c,s in [("Alias", "cyan"), ("ID", "green")]: t.add_column(c, s)
    for a,i in sorted(ms.items(), key=lambda x: (x[0] not in en, x[0])):
        if all or a in en: t.add_row(a, i[:40]+"..." if len(i)>40 else i)
    con.print(t); hist = []
    model = (c := typer.prompt("Model")).split(":")[0] if ":" in c and not c.startswith(("arn:", "us.")) else c if c.startswith(("arn:", "us.")) else ms.get(c)
    if not model: con.print("Model not found!"); return
    while (msg := typer.prompt("", prompt_suffix="You: ")) != "exit":
        if msg == "clear": hist = []; con.print("History cleared"); continue
        try: con.print("AI:", end=" "); r, hist = chat(rt, model, msg, hist); con.print() if r.strip() else con.print("No response")
        except Exception as e: con.print(f"Error: {e}")

if __name__ == "__main__": app()