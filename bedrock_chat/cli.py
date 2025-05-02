#!/usr/bin/env python3
import json,os,boto3,typer
from rich import console,live,markdown,table
from .__version__ import __version__
app,con=typer.Typer(),console.Console(highlight=False)
@app.command()
def main(clear:bool=False,all:bool=False,v:bool=typer.Option(False,"--version","-v"),p:str=typer.Option(None,"--profile"),r:str=typer.Option("us-east-1","--region"),allow:bool=typer.Option(False,"--allow-provisioned",help="Allow access to models requiring provisioned throughput (hourly $$$)")):
    if v:con.print(f"v{__version__}");return
    if clear:os.system("cls" if os.name=="nt" else "clear")
    s=boto3.Session(profile_name=p);rt,bd,ms,en,fmt=s.client("bedrock-runtime",region_name=r),s.client("bedrock",region_name=r),{},set(),{}
    test=lambda m:json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":1,"messages":[{"role":"user","content":[{"type":"text","text":"."}]}]} if "anthropic" in m.lower() or "claude" in m.lower() else {"inputText":".","textGenerationConfig":{"maxTokenCount":1}})
    with con.status("[cyan]Discovering models...[/cyan]"):
        for m in bd.list_foundation_models().get("modelSummaries",[]):
            if "TEXT" in [mode.upper() for mode in m.get("outputModalities",[])]:mid=m["modelId"];ms[mid.split(".")[-1].split("-v")[0]]=mid;fmt[mid]="chat" if "anthropic" in mid.lower() or "claude" in mid.lower() else "text"
            try:rt.invoke_model(modelId=mid,body=test(mid));en.add(mid.split(".")[-1].split("-v")[0])
            except:pass
        for p in bd.list_inference_profiles().get("inferenceProfileSummaries",[]):
            pid=p["inferenceProfileId"];n=pid.split(".")[-1]
            if any(t in pid.lower() for t in ["provisioned","throughput"]) and not allow:continue
            ms[n]=pid;fmt[pid]=fmt.get(p.get("modelId",""),"text")
            try:rt.invoke_model(modelId=pid,body=test(pid));en.add(n)
            except:pass
    t=table.Table(title=f"[bold cyan]Ultra Bedrock Chat v{__version__}[/bold cyan]",border_style="blue");[t.add_column(c,s) for c,s in [("Model","cyan"),("Type","yellow"),("ID","green")]];[t.add_row(n,"[bold red]Provisioned $[/bold red]" if any(t in i.lower() for t in ["provisioned","throughput"]) else "Inference Profile" if i.startswith("us.") else "On-Demand",i[:40]+"..." if len(i)>40 else i) for n,i in sorted(ms.items(),key=lambda x:(x[0] not in en,x[0])) if all or n in en]
    con.print(t);hist=[];inp=typer.prompt("Model");
    if inp.lower()=="exit":return
    if not (model:=inp if inp.startswith(("arn:","us.")) else ms.get(inp)):con.print("[bold red]Model not found![/bold red]");return
    if any(t in model.lower() for t in ["provisioned","throughput"]):con.print("[bold red]Warning:[/bold red] This model uses provisioned throughput which incurs hourly costs until explicitly deleted in AWS console")
    while (msg:=typer.prompt("",prompt_suffix="You: "))!="exit":
        if msg=="clear":hist=[];con.print("[italic green]History cleared[/italic green]");continue
        try:
            chat,txt=fmt.get(model,"text")=="chat","";body=json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":1024,"messages":hist+[{"role":"user","content":[{"type":"text","text":msg}]}]} if chat else {"inputText":msg,"textGenerationConfig":{"maxTokenCount":512}})
            with live.Live(markdown.Markdown("")) as l:
                for chunk in rt.invoke_model_with_response_stream(modelId=model,body=body).get("body"):
                    if "chunk" in chunk:d=json.loads(chunk["chunk"]["bytes"]);txt+=(d.get("delta",{}).get("text","") if "delta" in d else "".join([b.get("text","") for b in d.get("content",[]) if b.get("type")=="text"])) if chat else d.get("completion","");l.update(markdown.Markdown(txt))
            hist+=[{"role":"user","content":[{"type":"text","text":msg}]},{"role":"assistant","content":[{"type":"text","text":txt}]}] if txt.strip() else []
        except Exception as e:con.print(f"[bold red]Error:[/bold red] {e}")
if __name__=="__main__":app()