#!/usr/bin/env python3
"""从main.tex生成七模块合订PDF；--figures先编译实际引用的TikZ。"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,shutil,subprocess
ROOT=Path(__file__).resolve().parent
def run(args,cwd,log):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
 log.parent.mkdir(parents=True,exist_ok=True);log.write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(f'编译失败，参见 {log}')
def figure(f):
 src=ROOT/f['source'];dest=ROOT/f['output'];b=ROOT/'build/tikz'/src.relative_to(ROOT/'tikz').with_suffix('');b.mkdir(parents=True,exist_ok=True)
 run(['xelatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={b}',str(src)],ROOT,b/'console.log')
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(b/(src.stem+'.pdf'),dest)
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--figures',action='store_true');args=parser.parse_args()
 if not shutil.which('xelatex'):raise SystemExit('需要含XeLaTeX的TeX Live或MacTeX。')
 b=ROOT/'build';b.mkdir(exist_ok=True)
 if args.figures:
  fs=json.loads((ROOT/'figures.json').read_text());list(ThreadPoolExecutor(max_workers=3).map(figure,fs));print(f'已编译{len(fs)}张TikZ。',flush=True)
 if shutil.which('latexmk'):
  run(['latexmk','-norc','-xelatex','-interaction=nonstopmode','-halt-on-error','-outdir=build','main.tex'],ROOT,b/'console.log')
 else:
  for i in range(3):run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex'],ROOT,b/f'pass-{i+1}.log')
 dest=ROOT/'dist/电磁学二轮_七模块合订版.pdf';dest.parent.mkdir(exist_ok=True)
 if shutil.which('qpdf'):
  run(['qpdf','--object-streams=generate','--stream-data=compress',str(b/'main.pdf'),str(dest)],ROOT,b/'qpdf.log')
 else:shutil.copy2(b/'main.pdf',dest)
 print(f'已生成 {dest}',flush=True)
