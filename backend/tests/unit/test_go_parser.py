from app.services.parsing.parsers.go import GoParser


def test_go_parser_functions_structs_imports():
    code = """package main

import (
    "fmt"
    "net/http"
)

type Server struct {
    port int
}

func (s *Server) Start() error {
    return nil
}

func NewServer(port int) *Server {
    return &Server{port: port}
}
"""
    parser = GoParser()
    res = parser.parse("main.go", code)

    assert len(res.symbols) >= 3

    # Check struct
    struct_sym = next(s for s in res.symbols if s.name == "Server")
    assert struct_sym.kind == "struct"
    assert struct_sym.is_exported is True

    # Check method
    method_sym = next(s for s in res.symbols if s.name == "Start")
    assert method_sym.kind == "method"
    assert method_sym.is_exported is True

    # Check function
    func_sym = next(s for s in res.symbols if s.name == "NewServer")
    assert func_sym.kind == "function"

    # Check imports
    assert len(res.imports) == 2
    assert any(i.source == "fmt" for i in res.imports)
    assert any(i.source == "net/http" for i in res.imports)
