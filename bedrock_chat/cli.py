#!/usr/bin/env python3
import json,os,boto3,typer
from rich import console,live,markdown,table
from .__version__ import __version__
app,con=typer.Typer(),console.Console()
@app.callback(invoke_without_command=True)
def main(v:bool=typer.Option(False,"--version","-v"),p:str=typer.Option(None,"--profile"),r:str=typer.Option("us-east-1","--region"),c:typer.Context=typer.Context):
    if v:con.print(f"v{__version__}");raise typer.Exit()
    globals().update({"p":p,"r":r});c.invoked_subcommand or chat()
@app.command()
def chat(clear:bool=False,all:bool=False):
    if clear:os.system("cls" if os.name=="nt" else "clear")
    s=boto3.Session(profile_name=globals().get("p"));r=globals().get("r","us-east-1")
    rt,bd,ms,en=s.client("bedrock-runtime",region_name=r),s.client("bedrock",region_name=r),{},set()
    test=lambda m:json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":1,"messages":[{"role":"user","content":[{"type":"text","text":"."}]}]} if "anthropic" in m else {"inputText":".","textGenerationConfig":{"maxTokenCount":1}})
    with con.status("Loading..."):
        for m in bd.list_foundation_models().get("modelSummaries",[]):
            if "TEXT" in [mode.upper() for mode in m.get("outputModalities",[])]:a=m["modelId"].split(".")[-1].split("-v")[0];ms[a]=m["modelId"]
            try:rt.invoke_model(modelId=m["modelId"],body=test(m["modelId"]));en.add(a)
            except:pass
        try:
            for p in bd.list_inference_profiles().get("inferenceProfileSummaries",[]):a=p["inferenceProfileId"].split(".")[-1];ms[a]=p["inferenceProfileId"]
            try:rt.invoke_model(modelId=p["inferenceProfileId"],body=test(p["inferenceProfileId"]));en.add(a)
            except:pass
        except:pass
    t=table.Table();[t.add_column(c,s) for c,s in [("Model","cyan"),("ID","green")]];[t.add_row(a,i[:40]+"..." if len(i)>40 else i) for a,i in sorted(ms.items(),key=lambda x:(x[0] not in en,x[0])) if all or a in en]
    con.print(t);hist=[];model=(c:=typer.prompt("Model")) if c.startswith(("arn:","us.")) else ms.get(c)
    if not model:con.print("Model not found!");return
    while (msg:=typer.prompt("",prompt_suffix="You: "))!="exit":
        if msg=="clear":hist=[];con.print("History cleared");continue
        try:
            ic,txt="anthropic" in model,""
            body=json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":1024,"messages":hist+[{"role":"user","content":[{"type":"text","text":msg}]}]} if ic else {"inputText":msg,"textGenerationConfig":{"maxTokenCount":512}})
            with live.Live(markdown.Markdown("")) as l:
                for c in rt.invoke_model_with_response_stream(modelId=model,body=body).get("body"):
                    if "chunk" in c:d=json.loads(c["chunk"]["bytes"]);txt+=(d.get("delta",{}).get("text","") if "delta" in d else "".join([b.get("text","") for b in d.get("content",[]) if b.get("type")=="text"])) if ic else d.get("completion","");l.update(markdown.Markdown(txt))
            hist+=[{"role":"user","content":[{"type":"text","text":msg}]},{"role":"assistant","content":[{"type":"text","text":txt}]}] if txt.strip() else []
        except Exception as e:con.print(f"Error: {e}")
if __name__=="__main__":app()