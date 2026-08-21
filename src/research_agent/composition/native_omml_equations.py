"""
Master OMML Equation Registry with 100% Native Word Elements.
Zero SMP characters, zero raw delimiter mismatches, explicit <w:noProof/>.
"""

from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def make_evidence_space_omml():
    """Native OMML for Y subseteq {0, 1}^{|T|} using script style on ASCII Y and T."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>Y</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ⊆ </m:t></m:r>\n'
        '  <m:sSup>\n'
        '    <m:e>\n'
        '      <m:d>\n'
        '        <m:dPr><m:begChr m:val="{"/><m:endChr m:val="}"/><m:grow/></m:dPr>\n'
        '        <m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>0, 1</m:t></m:r></m:e>\n'
        '      </m:d>\n'
        '    </m:e>\n'
        '    <m:sup>\n'
        '      <m:r><m:rPr><m:nor/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>card</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '      <m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>T</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '    </m:sup>\n'
        '  </m:sSup>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_frequency_vector_omml():
    """Native OMML for x = [c(e1), c(e2), ..., c(eM)]^T in R^M with full delimiter containment."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>x</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSup>\n'
        '    <m:e>\n'
        '      <m:d>\n'
        '        <m:dPr><m:begChr m:val="["/><m:endChr m:val="]"/><m:grow/></m:dPr>\n'
        '        <m:e>\n'
        '          <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>c</m:t></m:r>\n'
        '          <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>1</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '          <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>c</m:t></m:r>\n'
        '          <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, ..., </m:t></m:r>\n'
        '          <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>c</m:t></m:r>\n'
        '          <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>M</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '        </m:e>\n'
        '      </m:d>\n'
        '    </m:e>\n'
        '    <m:sup><m:r><m:rPr><m:sty m:val="p"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>T</m:t></m:r></m:sup>\n'
        '  </m:sSup>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r>\n'
        '  <m:sSup>\n'
        '    <m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>R</m:t></m:r></m:e>\n'
        '    <m:sup><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>M</m:t></m:r></m:sup>\n'
        '  </m:sSup>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_inv_omml():
    """Native OMML for L_inv(P_seq, P_graph) = 1/B sum_{i=1}^B ||p_seq^(i) - p_graph^(i)||_2^2."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>inv</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>'
        '  </m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:num><m:r><w:rPr><w:noProof/></w:rPr><m:t>1</m:t></m:r></m:num><m:den><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>B</m:t></m:r></m:den></m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow/></m:naryPr>'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t>=1</m:t></m:r></m:sub>'
        '    <m:sup><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>B</m:t></m:r></m:sup>'
        '    <m:e>'
        '      <m:sSubSup>'
        '        <m:e><m:d><m:dPr><m:begChr m:val="‖"/><m:endChr m:val="‖"/><m:grow/></m:dPr><m:e>'
        '          <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub><m:sup><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r></m:e></m:d></m:sup></m:sSubSup>'
        '          <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>'
        '          <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub><m:sup><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r></m:e></m:d></m:sup></m:sSubSup>'
        '        </m:e></m:d></m:e>'
        '        <m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sub>'
        '        <m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sup>'
        '      </m:sSubSup>'
        '    </m:e>'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_var_omml():
    """Native OMML for L_var(P) = 1/d_proj sum_{j=1}^{d_proj} max(0, gamma - sqrt(Var(p_{:, j}) + eps))."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>var</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:num><m:r><w:rPr><w:noProof/></w:rPr><m:t>1</m:t></m:r></m:num><m:den><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>d</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>proj</m:t></m:r></m:sub></m:sSub></m:den></m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow/></m:naryPr>'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>j</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t>=1</m:t></m:r></m:sub>'
        '    <m:sup><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>d</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>proj</m:t></m:r></m:sub></m:sSub></m:sup>'
        '    <m:e>'
        '      <m:r><w:rPr><w:noProof/></w:rPr><m:t>max</m:t></m:r>'
        '      <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '        <m:r><w:rPr><w:noProof/></w:rPr><m:t>0, </m:t></m:r>'
        '        <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>γ</m:t></m:r>'
        '        <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>'
        '        <m:rad><m:radPr><m:degHide/></m:radPr><m:deg/><m:e>'
        '          <m:r><w:rPr><w:noProof/></w:rPr><m:t>Var</m:t></m:r>'
        '          <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>:, j</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '          <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>'
        '          <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>ϵ</m:t></m:r>'
        '        </m:e></m:rad>'
        '      </m:e></m:d>'
        '    </m:e>'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_var_formula_omml():
    """Native OMML for Var(p_{:, j}) = 1/(B-1) sum_{i=1}^B (p_{i, j} - bar{p}_j)^2."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t>Var</m:t></m:r>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>:, j</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:num><m:r><w:rPr><w:noProof/></w:rPr><m:t>1</m:t></m:r></m:num><m:den><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>B</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t> - 1</m:t></m:r></m:den></m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow/></m:naryPr>'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t>=1</m:t></m:r></m:sub>'
        '    <m:sup><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>B</m:t></m:r></m:sup>'
        '    <m:e>'
        '      <m:sSup>'
        '        <m:e><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '          <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i, j</m:t></m:r></m:sub></m:sSub>'
        '          <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>'
        '          <m:sSub><m:e><m:acc><m:accPr><m:chr m:val="¯"/></m:accPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e></m:acc></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub>'
        '        </m:e></m:d></m:e>'
        '        <m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sup>'
        '      </m:sSup>'
        '    </m:e>'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_c_matrix_omml():
    """Native OMML for C(P) = 1/(B-1) sum_{i=1}^B (p^(i) - bar{p})(p^(i) - bar{p})^T."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>C</m:t></m:r>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:num><m:r><w:rPr><w:noProof/></w:rPr><m:t>1</m:t></m:r></m:num><m:den><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>B</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t> - 1</m:t></m:r></m:den></m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow/></m:naryPr>'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t>=1</m:t></m:r></m:sub>'
        '    <m:sup><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>B</m:t></m:r></m:sup>'
        '    <m:e>'
        '      <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '        <m:sSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e><m:sup><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r></m:e></m:d></m:sup></m:sSup>'
        '        <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>'
        '        <m:acc><m:accPr><m:chr m:val="¯"/></m:accPr><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e></m:acc>'
        '      </m:e></m:d>'
        '      <m:sSup>'
        '        <m:e><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '          <m:sSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e><m:sup><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r></m:e></m:d></m:sup></m:sSup>'
        '          <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>'
        '          <m:acc><m:accPr><m:chr m:val="¯"/></m:accPr><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>p</m:t></m:r></m:e></m:acc>'
        '        </m:e></m:d></m:e>'
        '        <m:sup><m:r><m:rPr><m:sty m:val="p"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>T</m:t></m:r></m:sup>'
        '      </m:sSup>'
        '    </m:e>'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_cov_omml():
    """Native OMML for L_cov(P) = 1/d_proj sum_{j=1}^{d_proj} sum_{k ne j} (C_{j, k}(P))^2."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>cov</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:num><m:r><w:rPr><w:noProof/></w:rPr><m:t>1</m:t></m:r></m:num><m:den><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>d</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>proj</m:t></m:r></m:sub></m:sSub></m:den></m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow/></m:naryPr>'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>j</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t>=1</m:t></m:r></m:sub>'
        '    <m:sup><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>d</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>proj</m:t></m:r></m:sub></m:sSub></m:sup>'
        '    <m:e>'
        '      <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:supHide m:val="1"/><m:grow/></m:naryPr>'
        '        <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>k</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t> ≠ </m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>j</m:t></m:r></m:sub>'
        '        <m:e>'
        '          <m:sSup>'
        '            <m:e><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '              <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>C</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>j, k</m:t></m:r></m:sub></m:sSub>'
        '              <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e></m:d>'
        '            </m:e></m:d></m:e>'
        '            <m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sup>'
        '          </m:sSup>'
        '        </m:e>'
        '      </m:nary>'
        '    </m:e>'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_stage_a_loss_omml():
    """Native OMML for L_StageA = lambda_inv L_inv + lambda_var(L_var_seq + L_var_graph) + lambda_cov(L_cov_seq + L_cov_graph) + lambda_spec L_preserv + lambda_rec L_fuse-rec."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>Stage-A</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>λ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>inv</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>inv</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>λ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>var</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '    <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>var</m:t></m:r></m:sub></m:sSub>'
        '    <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>var</m:t></m:r></m:sub></m:sSub>'
        '    <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '  </m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>λ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>cov</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '    <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>cov</m:t></m:r></m:sub></m:sSub>'
        '    <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>cov</m:t></m:r></m:sub></m:sSub>'
        '    <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>P</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '  </m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>λ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>spec</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>preserv</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>λ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>rec</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>fuse-rec</m:t></m:r></m:sub></m:sSub>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_quality_vector_omml():
    """Native OMML for q_seq = [m_seq, Cov_event, Delta t_span]^T in R^3, q_graph = [m_graph, Cov_graph, Density_edge]^T in R^3."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>q</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSup><m:e><m:d><m:dPr><m:begChr m:val="["/><m:endChr m:val="]"/><m:grow/></m:dPr><m:e>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><w:rPr><w:noProof/></w:rPr><m:t>Cov</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>event</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><w:rPr><w:noProof/></w:rPr><m:t>Δ</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>t</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>span</m:t></m:r></m:sub></m:sSub>'
        '  </m:e></m:d></m:e><m:sup><m:r><m:rPr><m:sty m:val="p"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>T</m:t></m:r></m:sup></m:sSup>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> ∈ </m:t></m:r>\n'
        '  <m:sSup><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>3</m:t></m:r></m:sup></m:sSup>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>q</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSup><m:e><m:d><m:dPr><m:begChr m:val="["/><m:endChr m:val="]"/><m:grow/></m:dPr><m:e>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><w:rPr><w:noProof/></w:rPr><m:t>Cov</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><w:rPr><w:noProof/></w:rPr><m:t>Density</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>edge</m:t></m:r></m:sub></m:sSub>'
        '  </m:e></m:d></m:e><m:sup><m:r><m:rPr><m:sty m:val="p"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>T</m:t></m:r></m:sup></m:sSup>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> ∈ </m:t></m:r>\n'
        '  <m:sSup><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>3</m:t></m:r></m:sup></m:sSup>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_gating_weights_omml():
    """Native OMML for w_rel^seq = tau + (1 - 2*tau) * exp(s_seq)/(exp(s_seq) + exp(s_graph)), w_rel^graph = 1 - w_rel^seq."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>rel</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sup></m:sSubSup>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>τ</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>1 - 2</m:t></m:r>'
        '    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>τ</m:t></m:r>'
        '  </m:e></m:d>\n'
        '  <m:f><m:num>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>exp</m:t></m:r>'
        '    <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>s</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '  </m:num><m:den>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>exp</m:t></m:r>'
        '    <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>s</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>exp</m:t></m:r>'
        '    <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>s</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '  </m:den></m:f>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>\n'
        '  <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>rel</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sup></m:sSubSup>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = 1 - </m:t></m:r>\n'
        '  <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>rel</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sup></m:sSubSup>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_pcgrad_omml():
    """Native OMML for g_align <- g_align - <g_align, g_preserv>/||g_preserv||_2^2 g_preserv on Theta_shared."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>g</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>align</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> ← </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>g</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>align</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>\n'
        '  <m:f><m:num>'
        '    <m:d><m:dPr><m:begChr m:val="⟨"/><m:endChr m:val="⟩"/><m:grow/></m:dPr><m:e>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>g</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>align</m:t></m:r></m:sub></m:sSub>'
        '      <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>g</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>preserv</m:t></m:r></m:sub></m:sSub>'
        '    </m:e></m:d>'
        '  </m:num><m:den>'
        '    <m:sSubSup><m:e><m:d><m:dPr><m:begChr m:val="‖"/><m:endChr m:val="‖"/><m:grow/></m:dPr><m:e>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>g</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>preserv</m:t></m:r></m:sub></m:sSub>'
        '    </m:e></m:d></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sup></m:sSubSup>'
        '  </m:den></m:f>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>g</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>preserv</m:t></m:r></m:sub></m:sSub>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_mil_attention_omml():
    """Native OMML for a_i = exp(w^T(tanh(V z_i) odot sigma(U z_i))) / sum_j exp(...)."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>a</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:num>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>exp</m:t></m:r>'
        '    <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '      <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mil</m:t></m:r></m:sub><m:sup><m:r><m:rPr><m:sty m:val="p"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>T</m:t></m:r></m:sup></m:sSubSup>'
        '      <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '        <m:r><w:rPr><w:noProof/></w:rPr><m:t>tanh</m:t></m:r>'
        '        <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '          <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>V</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mil</m:t></m:r></m:sub></m:sSub>'
        '          <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub><m:sup><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r></m:e></m:d></m:sup></m:sSubSup>'
        '        </m:e></m:d>'
        '        <m:r><w:rPr><w:noProof/></w:rPr><m:t> ⊙ </m:t></m:r>'
        '        <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>σ</m:t></m:r>'
        '        <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '          <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>U</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mil</m:t></m:r></m:sub></m:sSub>'
        '          <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub><m:sup><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>i</m:t></m:r></m:e></m:d></m:sup></m:sSubSup>'
        '        </m:e></m:d>'
        '      </m:e></m:d>'
        '    </m:e></m:d>'
        '  </m:num><m:den>'
        '    <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow/></m:naryPr>'
        '      <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>j</m:t></m:r><m:r><w:rPr><w:noProof/></w:rPr><m:t>=1</m:t></m:r></m:sub>'
        '      <m:sup><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>K</m:t></m:r></m:sup>'
        '      <m:e>'
        '        <m:r><w:rPr><w:noProof/></w:rPr><m:t>exp</m:t></m:r>'
        '        <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '          <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mil</m:t></m:r></m:sub><m:sup><m:r><m:rPr><m:sty m:val="p"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>T</m:t></m:r></m:sup></m:sSubSup>'
        '          <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '            <m:r><w:rPr><w:noProof/></w:rPr><m:t>tanh</m:t></m:r>'
        '            <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '              <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>V</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mil</m:t></m:r></m:sub></m:sSub>'
        '              <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub><m:sup><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>j</m:t></m:r></m:e></m:d></m:sup></m:sSubSup>'
        '            </m:e></m:d>'
        '            <m:r><w:rPr><w:noProof/></w:rPr><m:t> ⊙ </m:t></m:r>'
        '            <m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>σ</m:t></m:r>'
        '            <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '              <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>U</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mil</m:t></m:r></m:sub></m:sSub>'
        '              <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub><m:sup><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>j</m:t></m:r></m:e></m:d></m:sup></m:sSubSup>'
        '            </m:e></m:d>'
        '          </m:e></m:d>'
        '        </m:e></m:d>'
        '      </m:e>'
        '    </m:nary>'
        '  </m:den></m:f>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_mil_loss_omml():
    """Native OMML for L_MIL = - Y_bag log(hat{Y}_bag) - (1 - Y_bag) log(1 - hat{Y}_bag)."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>MIL</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = - </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>Y</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>bag</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> log</m:t></m:r>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:acc><m:accPr><m:chr m:val="^"/></m:accPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>Y</m:t></m:r></m:e></m:acc></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>bag</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><w:rPr><w:noProof/></w:rPr><m:t>1 - </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>Y</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>bag</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> log</m:t></m:r>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:r><w:rPr><w:noProof/></w:rPr><m:t>1 - </m:t></m:r><m:sSub><m:e><m:acc><m:accPr><m:chr m:val="^"/></m:accPr><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>Y</m:t></m:r></m:e></m:acc></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>bag</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_canonical_fusion_omml():
    """Native OMML for z_mv = LayerNorm(m_seq w_rel^seq W_out^seq z_seq + m_graph w_rel^graph W_out^graph z_graph + m_seq m_graph W_out^cross u_cross)."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t>LayerNorm</m:t></m:r>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub>'
        '    <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>rel</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sup></m:sSubSup>'
        '    <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>out</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sup></m:sSubSup>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>'
        '    <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>rel</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sup></m:sSubSup>'
        '    <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>out</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sup></m:sSubSup>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>'
        '    <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>out</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>cross</m:t></m:r></m:sup></m:sSubSup>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>u</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>cross</m:t></m:r></m:sub></m:sSub>'
        '  </m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> ∈ </m:t></m:r>\n'
        '  <m:sSup><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>d</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub></m:sSub></m:sup></m:sSup>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_rep_bundle_omml():
    """Native OMML for B_mv = <z_mv, [t_start, t_end], E_scope, m_seq, m_graph, w_rel>."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>B</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:d><m:dPr><m:begChr m:val="⟨"/><m:endChr m:val="⟩"/><m:grow/></m:dPr><m:e>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:d><m:dPr><m:begChr m:val="["/><m:endChr m:val="]"/><m:grow/></m:dPr><m:e>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>t</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>start</m:t></m:r></m:sub></m:sSub>'
        '      <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>t</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>end</m:t></m:r></m:sub></m:sSub>'
        '    </m:e></m:d>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>E</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>scope</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>'
        '    <m:r><w:rPr><w:noProof/></w:rPr><m:t>, </m:t></m:r>'
        '    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>rel</m:t></m:r></m:sub></m:sSub>'
        '  </m:e></m:d>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)

def make_graph_self_loss_omml():
    """Native OMML for L_graph^self = beta_1 L_mask-node + beta_2 L_mask-edge + beta_3 L_time-gap."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSubSup><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>self</m:t></m:r></m:sup></m:sSubSup>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>β</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>1</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mask-node</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>β</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mask-edge</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>β</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>3</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>time-gap</m:t></m:r></m:sub></m:sSub>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_preserv_loss_omml():
    """Native OMML for L_preserv = L_seq^self(z_seq) + L_graph^self(z_graph)."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>preserv</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSubSup><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>self</m:t></m:r></m:sup></m:sSubSup>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSubSup><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>self</m:t></m:r></m:sup></m:sSubSup>\n'
        '  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub></m:e></m:d>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_fuse_rec_stopgrad_omml():
    """Native OMML for L_fuse-rec = ||D_seq z_mv - stopgrad(z_seq)||_2^2 + ||D_graph z_mv - stopgrad(z_graph)||_2^2."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>fuse-rec</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSubSup>\n'
        '    <m:e><m:d><m:dPr><m:begChr m:val="‖"/><m:endChr m:val="‖"/><m:grow/></m:dPr><m:e>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>D</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub></m:sSub>'
        '      <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>'
        '      <m:r><w:rPr><w:noProof/></w:rPr><m:t>stopgrad</m:t></m:r>'
        '      <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>seq</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '    </m:e></m:d></m:e>\n'
        '    <m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sub>\n'
        '    <m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sup>\n'
        '  </m:sSubSup>\n'
        '  <m:r><w:rPr><w:noProof/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSubSup>\n'
        '    <m:e><m:d><m:dPr><m:begChr m:val="‖"/><m:endChr m:val="‖"/><m:grow/></m:dPr><m:e>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>D</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mv</m:t></m:r></m:sub></m:sSub>'
        '      <m:r><w:rPr><w:noProof/></w:rPr><m:t> - </m:t></m:r>'
        '      <m:r><w:rPr><w:noProof/></w:rPr><m:t>stopgrad</m:t></m:r>'
        '      <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:grow/></m:dPr><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub></m:e></m:d>'
        '    </m:e></m:d></m:e>\n'
        '    <m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sub>\n'
        '    <m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sup>\n'
        '  </m:sSubSup>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_tgn_msg_omml():
    """Portable OMML for m_{v->u}(t) = Msg(h_{v,pre}, h_{u,pre}, Delta t_v(t), e_r, x_e)."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>→</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>Msg</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>,</m:t></m:r><m:r><m:rPr><m:nor/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>pre</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>,</m:t></m:r><m:r><m:rPr><m:nor/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>pre</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>Δ</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>r</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_tgn_agg_omml():
    """Portable OMML for m_{u,agg}(t) = Agg({m_{v->u}(t) : (v, u) in N_t(u)})."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>,</m:t></m:r><m:r><m:rPr><m:nor/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>agg</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>Agg</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>{</m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>→</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> : </m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>N</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>}</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_tgn_update_omml():
    """Portable OMML for h_u(t) = Update(h_{u,pre}, m_{u,agg}(t))."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>Update</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>,</m:t></m:r><m:r><m:rPr><m:nor/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>pre</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>m</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>,</m:t></m:r><m:r><m:rPr><m:nor/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>agg</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_tgn_readout_omml():
    """Portable OMML for z_graph = Readout_graph({h_u(t) : u in V_active(W_m)}) = sum ..."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>Readout</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>{</m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> : </m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>V</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>active</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>m</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>}</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '    <m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>V</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>active</m:t></m:r></m:sub></m:sSub></m:sub>\n'
        '    <m:e>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>softmax</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '        <m:f><m:fPr><m:type m:val="bar"/></m:fPr>\n'
        '          <m:num><m:sSup><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>w</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub></m:e><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>T</m:t></m:r></m:sup></m:sSup><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r></m:num>\n'
        '          <m:den><m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>d</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>GNN</m:t></m:r></m:sub></m:sSub></m:e></m:rad></m:den>\n'
        '        </m:f>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>gproj</m:t></m:r></m:sub></m:sSub>\n'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '    </m:e>\n'
        '  </m:nary>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r>\n'
        '  <m:sSup><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>d</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>graph</m:t></m:r></m:sub></m:sSub></m:sup></m:sSup>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_mep_omml():
    """Portable OMML for L_MEP = - 1/card(M_event) sum_{i in M_event} log [softmax(phi_seq^event(h_i))]_{tau_i}."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>MEP</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = -</m:t></m:r>\n'
        '  <m:f><m:fPr><m:type m:val="bar"/></m:fPr>\n'
        '    <m:num><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>1</m:t></m:r></m:num>\n'
        '    <m:den><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>card</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>M</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>event</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r></m:den>\n'
        '  </m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>M</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>event</m:t></m:r></m:sub></m:sSub></m:sub>\n'
        '    <m:e>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>log</m:t></m:r>\n'
        '      <m:sSub><m:e>\n'
        '        <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>[</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>softmax</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '            <m:sSubSup><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>φ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>seq</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>event</m:t></m:r></m:sup></m:sSubSup>\n'
        '            <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>seq</m:t></m:r></m:sup></m:sSubSup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '        <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>]</m:t></m:r>\n'
        '      </m:e><m:sub><m:sSub><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub></m:sub></m:sSub>\n'
        '    </m:e>\n'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_mpp_omml():
    """Portable OMML for L_MPP = 1/card(M_param) sum_{i in M_param} sum_{(k_j, v_j) in p_i^priv} ..."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:noProof/></m:rPr><m:t>MPP</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:fPr><m:type m:val="bar"/></m:fPr>\n'
        '    <m:num><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>1</m:t></m:r></m:num>\n'
        '    <m:den><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>card</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>M</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>param</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r></m:den>\n'
        '  </m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>M</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>param</m:t></m:r></m:sub></m:sSub></m:sub>\n'
        '    <m:e>\n'
        '      <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '        <m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>k</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>p</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>priv</m:t></m:r></m:sup></m:sSubSup></m:sub>\n'
        '        <m:e>\n'
        '          <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>ℓ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>param</m:t></m:r></m:sub></m:sSub>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '          <m:sSubSup><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>φ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>seq</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>param</m:t></m:r></m:sup></m:sSubSup>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>seq</m:t></m:r></m:sup></m:sSubSup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>k</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '        </m:e>\n'
        '      </m:nary>\n'
        '    </m:e>\n'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_seq_time_omml():
    """Portable OMML for L_time = 1/card(M_time) sum_{i in M_time} l_delta(phi_seq^time(h_i), log(1 + Delta t_i))."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>time</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:fPr><m:type m:val="bar"/></m:fPr>\n'
        '    <m:num><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>1</m:t></m:r></m:num>\n'
        '    <m:den><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>card</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>M</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>time</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r></m:den>\n'
        '  </m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>M</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>time</m:t></m:r></m:sub></m:sSub></m:sub>\n'
        '    <m:e>\n'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>ℓ</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>δ</m:t></m:r></m:sub></m:sSub>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '      <m:sSubSup><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>φ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>seq</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>time</m:t></m:r></m:sup></m:sSubSup>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>seq</m:t></m:r></m:sup></m:sSubSup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>log</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>1 + </m:t></m:r>\n'
        '      <m:sSub><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>Δ</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '    </m:e>\n'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_mask_node_omml():
    """Portable OMML for L_mask-node = 1/card(V_mask) sum_{v in V_mask} ||phi_graph^node(h_v(t)) - x_v^priv||_2^2."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mask-node</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:fPr><m:type m:val="bar"/></m:fPr>\n'
        '    <m:num><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>1</m:t></m:r></m:num>\n'
        '    <m:den><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>card</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>V</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>mask</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r></m:den>\n'
        '  </m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '    <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>V</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>mask</m:t></m:r></m:sub></m:sSub></m:sub>\n'
        '    <m:e>\n'
        '      <m:sSubSup>\n'
        '        <m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>‖</m:t></m:r>\n'
        '          <m:sSubSup><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>φ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>graph</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>node</m:t></m:r></m:sup></m:sSubSup>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> - </m:t></m:r>\n'
        '          <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>priv</m:t></m:r></m:sup></m:sSubSup>\n'
        '        <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>‖</m:t></m:r></m:e>\n'
        '        <m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sub>\n'
        '        <m:sup><m:r><w:rPr><w:noProof/></w:rPr><m:t>2</m:t></m:r></m:sup>\n'
        '      </m:sSubSup>\n'
        '    </m:e>\n'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_mask_edge_omml():
    """Portable OMML for L_mask-edge = - 1/card(E_mask) sum_{(v,u) in E_mask} log [softmax(phi_graph^edge([h_v(t); h_u(t)]))]_{r_{(v,u)}}."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/></w:rPr><m:t>mask-edge</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = -</m:t></m:r>\n'
        '  <m:f><m:fPr><m:type m:val="bar"/></m:fPr>\n'
        '    <m:num><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>1</m:t></m:r></m:num>\n'
        '    <m:den><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>card</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>E</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>mask</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r></m:den>\n'
        '  </m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '    <m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>E</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>mask</m:t></m:r></m:sub></m:sSub></m:sub>\n'
        '    <m:e>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>log</m:t></m:r>\n'
        '      <m:sSub><m:e>\n'
        '        <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>[</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>softmax</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '            <m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>φ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>graph</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>edge</m:t></m:r></m:sup></m:sSubSup>\n'
        '            <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '              <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>[</m:t></m:r>\n'
        '                <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '                <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>; </m:t></m:r>\n'
        '                <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '              <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>]</m:t></m:r>\n'
        '            <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '        <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>]</m:t></m:r>\n'
        '      </m:e><m:sub><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>r</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r></m:sub></m:sSub></m:sub></m:sSub>\n'
        '    </m:e>\n'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_l_time_gap_omml():
    """Portable OMML for L_time-gap = 1/card(E_active) sum_{(v,u) in E_active} l_delta(phi_graph^time([h_v(t); h_u(t)]), log(1 + Delta t_{v, u}))."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>L</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>time-gap</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:f><m:fPr><m:type m:val="bar"/></m:fPr>\n'
        '    <m:num><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>1</m:t></m:r></m:num>\n'
        '    <m:den><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>card</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>E</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>active</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r></m:den>\n'
        '  </m:f>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '    <m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:scr m:val="script"/><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>E</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>active</m:t></m:r></m:sub></m:sSub></m:sub>\n'
        '    <m:e>\n'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>ℓ</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>δ</m:t></m:r></m:sub></m:sSub>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '      <m:sSubSup><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>φ</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>graph</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>time</m:t></m:r></m:sup></m:sSubSup>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '        <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>[</m:t></m:r>\n'
        '          <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '          <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>; </m:t></m:r>\n'
        '          <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>h</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '        <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>]</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>log</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>1 + </m:t></m:r>\n'
        '      <m:sSub><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>Δ</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>,</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>u</m:t></m:r></m:sub></m:sSub>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '      <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '    </m:e>\n'
        '  </m:nary>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)


def make_event_embedding_omml():
    """Portable OMML for x_i = e_tau(tau_i) + e_a(a_i) + e_v(pi_psi(v_i)) + e_o(pi_psi(o_i)) + sum e_p(k_j, v_j) + e_time(t_i) + e_pos(i)."""
    xml_str = (
        f'<m:oMath {nsdecls("m", "w")}>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> = </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>τ</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>a</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>a</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>π</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>ψ</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>o</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>π</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>ψ</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>o</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/><m:grow m:val="1"/><m:subHide m:val="0"/><m:supHide m:val="1"/></m:naryPr>\n'
        '    <m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>k</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> ∈ </m:t></m:r><m:sSubSup><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>p</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub><m:sup><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>priv</m:t></m:r></m:sup></m:sSubSup></m:sub>\n'
        '    <m:e>\n'
        '      <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>p</m:t></m:r></m:sub></m:sSub>\n'
        '        <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>k</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>, </m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '    </m:e>\n'
        '  </m:nary>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>time</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>t</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t> + </m:t></m:r>\n'
        '  <m:sSub><m:e><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>e</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>pos</m:t></m:r></m:sub></m:sSub>\n'
        '  <m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>(</m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>i</m:t></m:r><m:r><w:rPr><w:noProof/><w:lang w:val="en-US"/></w:rPr><m:t>)</m:t></m:r>\n'
        '</m:oMath>'
    )
    return parse_xml(xml_str)
