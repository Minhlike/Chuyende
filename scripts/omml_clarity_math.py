"""Build editable, structured Word OMML for the worked examples.

This follows the existing thesis builders' LaTeX -> MathML -> Office
MML2OMML.XSL route.  Every expression is reviewed and mapped explicitly;
there is no generic wrapper that places raw notation in one m:t run.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from lxml import etree
from latex2mathml.converter import convert


EXAMPLES: dict[str, str] = {
    'Wᵀz+b=0': r'W^{\mathsf{T}}z+b=0',
    'σ(0)=0,5': r'\sigma(0)=0{,}5',
    'x=(2,1)ᵀ': r'x=(2,1)^{\mathsf{T}}',
    'log(1+10/2)=log 6': r'\log\left(1+\frac{10}{2}\right)=\log(6)',
    'log(1+10/10)=log 2': r'\log\left(1+\frac{10}{10}\right)=\log(2)',
    '0 log₂ 0=0': r'0\log_2 0=0',
    'H(W)=−[0,5 log₂(0,5)+0,5 log₂(0,5)]=1 bit': r'H(W)=-\left[0{,}5\,\log_2(0{,}5)+0{,}5\,\log_2(0{,}5)\right]=1\ \mathrm{bit}',
    'x=(3,2)ᵀ, P=(1,0)ᵀ': r'x=(3,2)^{\mathsf{T}},\quad P=(1,0)^{\mathsf{T}}',
    'xₐ=(0,2)ᵀ, ‖xₐ‖²=4': r'x_a=(0,2)^{\mathsf{T}},\quad \lVert x_a\rVert^2=4',
    'A=[1,−1], x=(2,2)ᵀ': r'A=[1,-1],\quad x=(2,2)^{\mathsf{T}}',
    'Ax=0': r'Ax=0',
    '0,79>0,80−0,02': r'0{,}79>0{,}80-0{,}02',
    'twm=100−5=95 giây': r't_{\mathrm{wm}}=100-5=95\ \mathrm{s}',
    'xᵢ=(1,1)': r'x_i=(1,1)',
    '−ln(0,8)≈0,223': r'-\ln(0{,}8)\approx0{,}223',
    'Pᵢᵐᵃˢᵏ': r'P_i^{\mathrm{mask}}',
    '[−ln(0,8)−ln(0,5)]/2≈0,458': r'\frac{-\ln(0{,}8)-\ln(0{,}5)}{2}\approx0{,}458',
    'ln(3)≈1,099': r'\ln(3)\approx1{,}099',
    'h₁=(1,0), h₂=(0,2), Wproj=I': r'h_1=(1,0),\quad h_2=(0,2),\quad W_{\mathrm{proj}}=I',
    'zseq=(0,25;1,5)': r'z_{\mathrm{seq}}=(0{,}25;1{,}5)',
    'exp(−ln 2)=0,5': r'\exp(-\ln 2)=0{,}5',
    '(1−1)²+(2−1)²=1': r'(1-1)^2+(2-1)^2=1',
    'zgraph=(0,5;1)': r'z_{\mathrm{graph}}=(0{,}5;1)',
    'Linv=(1+0)/2=0,5': r'L_{\mathrm{inv}}=\frac{1+0}{2}=0{,}5',
    'Lcov=(2²+2²)/2=4': r'L_{\mathrm{cov}}=\frac{2^2+2^2}{2}=4',
    'LStage-A=25×0,1+25×(0,1+0,1)+0,2+0,3=8,0': r'L_{\mathrm{Stage\text{-}A}}=25\times0{,}1+25\times(0{,}1+0{,}1)+0{,}2+0{,}3=8{,}0',
    'wrelseq=0,05+0,90×1/(1+3)=0,275': r'w_{\mathrm{rel,seq}}=0{,}05+0{,}90\times\frac{1}{1+3}=0{,}275',
    'galign=(1,−1), gpreserv=(−1,0)': r'g_{\mathrm{align}}=(1,-1),\quad g_{\mathrm{preserv}}=(-1,0)',
    'galign,proj=(0,−1)': r'g_{\mathrm{align,proj}}=(0,-1)',
    '−ln(0,5)≈0,693': r'-\ln(0{,}5)\approx0{,}693',
    'useq=(1,2), ugraph=(3,4)': r'u_{\mathrm{seq}}=(1,2),\quad u_{\mathrm{graph}}=(3,4)',
    'ucross=(3,8)': r'u_{\mathrm{cross}}=(3,8)',
    'Nlayers': r'N_{\mathrm{layers}}',
    'dff': r'd_{\mathrm{ff}}',
    'E_W': r'E_W',
    'Vupd': r'V_{\mathrm{upd}}',
    'dseq': r'd_{\mathrm{seq}}',
    'dgraph': r'd_{\mathrm{graph}}',
    'dmodel': r'd_{\mathrm{model}}',
    'dproj': r'd_{\mathrm{proj}}',
    'dcross': r'd_{\mathrm{cross}}',
    'datt': r'd_{\mathrm{att}}',
    'dmv': r'd_{\mathrm{mv}}',
    'Wproj': r'W_{\mathrm{proj}}',
    'Lpreserv': r'L_{\mathrm{preserv}}',
    'Lfuse-rec': r'L_{\mathrm{fuse\text{-}rec}}',
    'Linv': r'L_{\mathrm{inv}}',
    'Lvar': r'L_{\mathrm{var}}',
    'Lcov': r'L_{\mathrm{cov}}',
    'LStage-A': r'L_{\mathrm{Stage\text{-}A}}',
    'qseq': r'q_{\mathrm{seq}}',
    'qgraph': r'q_{\mathrm{graph}}',
    'sseq': r's_{\mathrm{seq}}',
    'sgraph': r's_{\mathrm{graph}}',
    'wrelseq': r'w_{\mathrm{rel,seq}}',
    'wrelgraph': r'w_{\mathrm{rel,graph}}',
    'zseq': r'z_{\mathrm{seq}}',
    'zgraph': r'z_{\mathrm{graph}}',
    'zbag': r'z_{\mathrm{bag}}',
    'zmv': r'z_{\mathrm{mv}}',
    'useq': r'u_{\mathrm{seq}}',
    'ugraph': r'u_{\mathrm{graph}}',
    'ucross': r'u_{\mathrm{cross}}',
    'galign': r'g_{\mathrm{align}}',
    'gpreserv': r'g_{\mathrm{preserv}}',
    'Cov_event': r'\operatorname{Cov}_{\mathrm{event}}',
    'Cov_graph': r'\operatorname{Cov}_{\mathrm{graph}}',
    'Density_edge': r'\operatorname{Density}_{\mathrm{edge}}',
    'Cstep': r'C_{\mathrm{step}}',
    'Cseq': r'C_{\mathrm{seq}}',
    'Cgraph': r'C_{\mathrm{graph}}',
    'Cstate': r'C_{\mathrm{state}}',
    'Calign': r'C_{\mathrm{align}}',
    'Mmax': r'M_{\mathrm{max}}',
    'Tbudget': r'T_{\mathrm{budget}}',
    'εinv': r'\varepsilon_{\mathrm{inv}}',
    'εmargin': r'\varepsilon_{\mathrm{margin}}',
}

XSLT = Path(r'C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL')
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'


@lru_cache(maxsize=1)
def transform() -> etree.XSLT:
    return etree.XSLT(etree.parse(str(XSLT)))


def make_example(raw: str) -> etree._Element:
    try:
        tex = EXAMPLES[raw]
    except KeyError as exc:
        raise ValueError(f'Unreviewed equation example: {raw}') from exc
    mathml = etree.fromstring(convert(tex).encode('utf-8'))
    omml = transform()(mathml).getroot()
    if omml.tag != M + 'oMath' or not list(omml.iter(M + 't')):
        raise ValueError(f'Invalid Office math conversion: {raw}')
    return omml
