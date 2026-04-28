from app.parsers.form4 import parse_form4


def test_parse_form4_extracts_owner_and_footnote():
    xml = """
    <ownershipDocument>
      <reportingOwner>
        <reportingOwnerId><rptOwnerCik>0001000</rptOwnerCik><rptOwnerName>Jane Doe</rptOwnerName></reportingOwnerId>
        <reportingOwnerRelationship><isDirector>1</isDirector><isOfficer>0</isOfficer></reportingOwnerRelationship>
      </reportingOwner>
      <footnotes><footnote id='F1'>Example</footnote></footnotes>
    </ownershipDocument>
    """
    parsed = parse_form4(xml)
    assert parsed["owners"][0]["owner_name"] == "Jane Doe"
    assert parsed["footnotes"][0]["footnote_id"] == "F1"
