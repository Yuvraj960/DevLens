# V2 Gamechanger Intelligence Suite (docs/v2_gamechanger.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

Phase 6 introduces the V2 Gamechanger features of **DevLens**: AI Code Review Agent, AST Refactoring Engine, Commit Timeline Narrator, Architecture Diff Engine, AI Onboarding Path Generator, and Interactive Dependency Graph.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ AI Code Review  │    │ AST Refactor    │    │ Commit Timeline │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
                       Gamechanger Engine
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Arch Diff       │    │ AI Onboarding   │    │ Dependency Graph│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## V2 Gamechanger Modules

1. **AI Code Review Agent (`code_reviewer.py`)**: Multi-agent review passes (`security`, `performance`, `correctness`, `maintainability`).
2. **AST Refactoring Engine (`refactor_engine.py`)**: Computes cyclomatic complexity and generates code diff proposals.
3. **Commit Timeline Narrator (`timeline_generator.py`)**: Groups git history into chronological architectural era summaries.
4. **Architecture Diff (`arch_diff.py`)**: Compares base vs head branch changes for API endpoints and ORM schema breaks.
5. **AI Onboarding Path (`onboarding_generator.py`)**: Topological sort of domain models into a step-by-step developer reading path.
6. **Interactive Dependency Graph (`dependency_graph_builder.py`)**: Full symbol import graph canvas.

---

## Quick Node Connections
- Flagship Execution Trace: [Flagship Execution Trace Engine](trace.md)
- System Architecture: [System Architecture & Intelligence](architecture.md)
- API Contracts: [API Contracts](api.md)
