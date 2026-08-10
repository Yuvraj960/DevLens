from app.services.parsing.parsers.typescript import TSParser


def test_ts_parser_functions_and_classes():
    code = """
export async function fetchUserData(userId: string): Promise<User> {
    return api.get(`/users/${userId}`);
}

export class UserService {
    private db: Database;
    constructor() {}
}

export interface User {
    id: string;
    name: string;
}

import { api } from '@/lib/api';
"""
    parser = TSParser()
    res = parser.parse("src/user.ts", code)

    assert len(res.symbols) == 3

    # Check function
    fn_sym = next(s for s in res.symbols if s.kind == "function")
    assert fn_sym.name == "fetchUserData"
    assert fn_sym.is_async is True
    assert fn_sym.is_exported is True

    # Check class
    cls_sym = next(s for s in res.symbols if s.kind == "class")
    assert cls_sym.name == "UserService"

    # Check interface
    if_sym = next(s for s in res.symbols if s.kind == "interface")
    assert if_sym.name == "User"

    # Check import
    assert len(res.imports) == 1
    assert res.imports[0].imported_symbol == "api"
    assert res.imports[0].source == "@/lib/api"
