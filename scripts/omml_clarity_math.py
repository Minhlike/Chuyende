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
    # Inline references in explanations must use the same Word math alphabet,
    # real subscript/superscript structures and upright function names as the
    # surrounding original equations.  Unicode faux subscripts are forbidden.
    'P_t': r'P_t',
    'X': r'X', 'Y': r'Y', 'z': r'z', 't': r't',
    'x': r'x', 'W': r'W', 'M': r'M', 'N': r'N', 'P': r'P',
    'I': r'I', 'A': r'A', 'B': r'B', 'C': r'C', 'F': r'F', 'K': r'K', 'L': r'L',
    'd': r'd', 'b': r'b', 'g': r'g', 'u': r'u', 'v': r'v',
    'σ': r'\sigma', 'γ': r'\gamma', 'ε': r'\varepsilon',
    'λ': r'\lambda', 'ϕ': r'\varphi', 'ψ': r'\psi',
    'τ': r'\tau', '⊥': r'\perp', '∀t': r'\forall t',
    'n(eᵢ)': r'n(e_i)', 'p(eᵢ)': r'p(e_i)',
    'eᵢ': r'e_i', 'N=10': r'N=10',
    'p(A)=p(B)=0,5': r'p(A)=p(B)=0{,}5',
    'H(W)=0': r'H(W)=0',
    'xₐ': r'x_a', '(3,0)ᵀ': r'(3,0)^{\top}',
    'γα=3': r'\gamma_\alpha=3',
    '4>3': r'4>3',
    'Ax=1': r'Ax=1', 'g=2': r'g=2',
    'Eₜ': r'E_t', 'Eₜ={A,B}': r'E_t=\{A,B\}',
    'Tᵥ': r'T_v', 'Tₑ': r'T_e',
    'Sₜ₋₁': r'S_{t-1}', 'eₜ': r'e_t', 'Sₜ': r'S_t',
    'fθ': r'f_\theta', 'zₜ': r'z_t',
    'Δt(eₜ)': r'\Delta t(e_t)', 'Mem(Sₜ)': r'\operatorname{Mem}(S_t)',
    '|Sₜ|': r'\lvert S_t\rvert',
    'τTTL': r'\tau_{\mathrm{TTL}}', 'δdelay': r'\delta_{\mathrm{delay}}',
    'τTTL=5': r'\tau_{\mathrm{TTL}}=5',
    'δdelay=5': r'\delta_{\mathrm{delay}}=5',
    'tlast(v)': r't_{\mathrm{last}}(v)',
    'Retain(x)': r'\operatorname{Retain}(x)',
    'Normalize(x)=ϕ(x)': r'\operatorname{Normalize}(x)=\varphi(x)',
    'πψ': r'\pi_\psi', 'pᵢ': r'p_i',
    'Wₛ': r'W_s', 'Wₘ': r'W_m', 'Wₗ': r'W_l',
    'xᵢ': r'x_i', 'Mₑᵥₑₙₜ': r'M_{\mathrm{event}}',
    '|Mₑᵥₑₙₜ|': r'\lvert M_{\mathrm{event}}\rvert',
    'τᵢ': r'\tau_i', 'Δtᵢ': r'\Delta t_i',
    'log(1+Δtᵢ)': r'\log(1+\Delta t_i)',
    'Lδ': r'L_\delta', 'δ=1': r'\delta=1',
    'Δtᵢ=2': r'\Delta t_i=2',
    'αᵢ': r'\alpha_i', 'hᵢ': r'h_i',
    't≥tₑ': r't\geq t_e', 'λ=ln(2)': r'\lambda=\ln(2)',
    'ε=10⁻⁴': r'\varepsilon=10^{-4}', 'B≥2': r'B\geq2',
    'B=2': r'B=2', 'γ=1': r'\gamma=1',
    'C(P)': r'C(P)', 'p_:,j': r'p_{:,j}',
    'dproj×dproj': r'd_{\mathrm{proj}}\times d_{\mathrm{proj}}',
    'ρoverlap': r'\rho_{\mathrm{overlap}}',
    'ρoverlap=0,5': r'\rho_{\mathrm{overlap}}=0{,}5',
    'τ=0,05': r'\tau=0{,}05',
    'Linv=2': r'L_{\mathrm{inv}}=2',
    'Linv=0,1': r'L_{\mathrm{inv}}=0{,}1',
    'Lpreserv=0,2': r'L_{\mathrm{preserv}}=0{,}2',
    'Lfuse-rec=0,3': r'L_{\mathrm{fuse\text{-}rec}}=0{,}3',
    'sseq=0': r's_{\mathrm{seq}}=0',
    'sgraph=ln 3': r's_{\mathrm{graph}}=\ln 3',
    'mseq': r'm_{\mathrm{seq}}', 'mgraph': r'm_{\mathrm{graph}}',
    'Pfuse': r'P_{\mathrm{fuse}}', 'Wout': r'W_{\mathrm{out}}',
    'q': r'q', 'O': r'O',
    'Update': r'\operatorname{Update}',
    'Msg': r'\operatorname{Msg}', 'Agg': r'\operatorname{Agg}',
    'ParamProtect': r'\operatorname{ParamProtect}',
    'Readoutgraph': r'\operatorname{Readout}_{\mathrm{graph}}',
    'Wᵀz+b=0': r'W^{\top}z+b=0',
    'σ(0)=0,5': r'\sigma(0)=0{,}5',
    'x=(2,1)ᵀ': r'x=(2,1)^{\top}',
    'log(1+10/2)=log 6': r'\log\left(1+\frac{10}{2}\right)=\log(6)',
    'log(1+10/10)=log 2': r'\log\left(1+\frac{10}{10}\right)=\log(2)',
    '0 log₂ 0=0': r'0\log_2 0=0',
    'H(W)=−[0,5 log₂(0,5)+0,5 log₂(0,5)]=1 bit': r'H(W)=-\left[0{,}5\,\log_2(0{,}5)+0{,}5\,\log_2(0{,}5)\right]=1\ \mathrm{bit}',
    'x=(3,2)ᵀ, P=(1,0)ᵀ': r'x=(3,2)^{\top},\quad P=(1,0)^{\top}',
    'xₐ=(0,2)ᵀ, ‖xₐ‖²=4': r'x_a=(0,2)^{\top},\quad \lVert x_a\rVert^2=4',
    'A=[1,−1], x=(2,2)ᵀ': r'A=[1,-1],\quad x=(2,2)^{\top}',
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
    'wrelseq=0,05+0,90×1/(1+3)=0,275': r'w_{\mathrm{rel}}^{\mathrm{seq}}=0{,}05+0{,}90\times\frac{1}{1+3}=0{,}275',
    'galign=(1,−1), gpreserv=(−1,0)': r'g_{\mathrm{align}}=(1,-1),\quad g_{\mathrm{preserv}}=(-1,0)',
    'galign^proj=(0,−1)': r'g_{\mathrm{align}}^{\mathrm{proj}}=(0,-1)',
    '(0,−1)': r'(0,-1)',
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
    'wrelseq': r'w_{\mathrm{rel}}^{\mathrm{seq}}',
    'wrelgraph': r'w_{\mathrm{rel}}^{\mathrm{graph}}',
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
