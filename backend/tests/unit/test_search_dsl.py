from app.services.search.dsl_parser import DSLParser


def test_dsl_query_parser():
    raw = "kind:function import:express name:auth* loc>50"
    parsed = DSLParser.parse_query_terms(raw)

    assert parsed["kind"] == "function"
    assert parsed["import_source"] == "express"
    assert parsed["name_pattern"] == "auth%"
    assert parsed["min_loc"] == 50
