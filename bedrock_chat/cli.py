#!/usr/bin/env python3
import json,os,boto3,typer
from rich import console,live,markdown,table
from .__version__ import __version__
app,con=typer.Typer(rich_markup_mode="rich"),console.Console(highlight=False)
@app.callback(invoke_without_command=True)
def main(v:bool=typer.Option(False,"--version","-v"),p:str=typer.Option(None,"--profile"),r:str=typer.Option("us-east-1","--region"),a:bool=typer.Option(False,"--allow-provisioned",help="Allow access to models requiring provisioned throughput (hourly $$$)"),c:typer.Context=typer.Context):
    if v:con.print(f"v{__version__}");raise typer.Exit()
    globals().update({"p":p,"r":r,"a":a});c.invoked_subcommand or chat()
@app.command()
def chat(clear:bool=False,all:bool=False):
    if clear:os.system("cls" if os.name=="nt" else "clear")
    s=boto3.Session(profile_name=globals().get("p"));r=globals().get("r","us-east-1")
    allow_provisioned=globals().get("a",False) # Get the allow-provisioned flag
    rt,bd,ms,en=s.client("bedrock-runtime",region_name=r),s.client("bedrock",region_name=r),{},set()
    test=lambda m:json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":1,"messages":[{"role":"user","content":[{"type":"text","text":"."}]}]} if "anthropic" in m else {"inputText":".","textGenerationConfig":{"maxTokenCount":1}})
    with con.status("[cyan]Discovering models...[/cyan]"):
        # Get foundation models
        for m in bd.list_foundation_models().get("modelSummaries",[]):
            if "TEXT" in [mode.upper() for mode in m.get("outputModalities",[])]:a=m["modelId"].split(".")[-1].split("-v")[0];ms[a]=m["modelId"]
            try:rt.invoke_model(modelId=m["modelId"],body=test(m["modelId"]));en.add(a)
            except:pass
        
        # Get inference profiles from user's configured region
        try:
            for prof in bd.list_inference_profiles().get("inferenceProfileSummaries",[]):
                # Handle inference profiles correctly
                prof_id = prof["inferenceProfileId"]
                name = prof_id.split(".")[-1] # Get the base name without the "us." prefix
                
                # Check if it's a provisioned throughput model
                is_provisioned = any(prov_term in prof_id.lower() for prov_term in ["provisioned", "throughput"]) or "claude-3-7" in prof_id.lower()
                
                # Skip provisioned models unless --allow-provisioned flag is set
                if is_provisioned and not allow_provisioned:
                    continue
                    
                ms[name]=prof_id
                try:rt.invoke_model(modelId=prof_id,body=test(prof_id));en.add(name)
                except:pass
        except:pass
    
    t=table.Table(title=f"[bold cyan]Ultra Bedrock Chat v{__version__}[/bold cyan]", border_style="blue")
    [t.add_column(c,style=s) for c,s in [("Model","cyan"),("Type","yellow"),("ID","green")]]
    for a,i in sorted(ms.items(),key=lambda x:(x[0] not in en,x[0])):
        if all or a in en:
            # Determine model type
            model_type = "On-Demand"
            if i.startswith("us."):
                # Check if it's a provisioned throughput model
                if any(prov_term in i.lower() for prov_term in ["provisioned", "throughput"]) or "claude-3-7" in i.lower():
                    model_type = "[bold red]Provisioned $[/bold red]"
                else:
                    model_type = "Inference Profile"
            t.add_row(a, model_type, i[:40]+"..." if len(i)>40 else i)
    con.print(t);hist=[];inp=typer.prompt("Model")
    if inp.lower() == "exit":return
    model=inp if inp.startswith(("arn:","us.")) else ms.get(inp)
    if not model:con.print("[bold red]Model not found![/bold red]");return
    # Warn about provisioned throughput costs
    if any(prov_term in model.lower() for prov_term in ["provisioned", "throughput"]) or "claude-3-7" in model.lower():
        con.print("[bold red]Warning:[/bold red] This model uses provisioned throughput which incurs hourly costs until explicitly deleted in AWS console")
    while (msg:=typer.prompt("",prompt_suffix="You: "))!="exit":
        if msg=="clear":hist=[];con.print("[italic green]History cleared[/italic green]");continue
        try:
            ic,txt="anthropic" in model,""
            body=json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":1024,"messages":hist+[{"role":"user","content":[{"type":"text","text":msg}]}]} if ic else {"inputText":msg,"textGenerationConfig":{"maxTokenCount":512}})
            with live.Live(markdown.Markdown("")) as l:
                for chunk in rt.invoke_model_with_response_stream(modelId=model,body=body).get("body"):
                    if "chunk" in chunk:d=json.loads(chunk["chunk"]["bytes"]);txt+=(d.get("delta",{}).get("text","") if "delta" in d else "".join([b.get("text","") for b in d.get("content",[]) if b.get("type")=="text"])) if ic else d.get("completion","");l.update(markdown.Markdown(txt))
            hist+=[{"role":"user","content":[{"type":"text","text":msg}]},{"role":"assistant","content":[{"type":"text","text":txt}]}] if txt.strip() else []
        except Exception as e:con.print(f"[bold red]Error:[/bold red] {e}")
if __name__=="__main__":app()