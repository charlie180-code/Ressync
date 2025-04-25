# Contributing to RESSYNC

Thank you for contributing to Ressync! This guide outlines our branching strategy and contribution workflow.

---

## **Branching Strategy**
We follow a structured branching model to ensure clean collaboration and organized development.

### **Branching Strategies Overview**
| **Branch Type**   | **Purpose**                                                                 | **Branch From** | **Merge Into** | **Naming Convention**         | **Example Command**                                                                 |
|--------------------|-----------------------------------------------------------------------------|-----------------|----------------|--------------------------------|-------------------------------------------------------------------------------------|
| `main`            | Stable, production-ready code.                                             | -               | -              | `main`                         | -                                                                                   |
| `develop`         | Integration branch for testing features before release.                    | `main`          | `release`      | `develop`                      | `git checkout main && git checkout -b develop`                                     |
| `feature`         | New feature development.                                                   | `develop`       | `develop`      | `feature/<feature-name>`       | `git checkout develop && git checkout -b feature/user-authentication`              |
| `hotfix`          | Quick fixes for critical bugs in production.                              | `main`          | `main`         | `hotfix/<fix-name>`            | `git checkout main && git checkout -b hotfix/critical-fix`                         |
| `bugfix`          | Fixes for bugs found during active development.                           | `develop`       | `develop`      | `bugfix/<fix-name>`            | `git checkout develop && git checkout -b bugfix/login-bug`                         |
| `release`         | Preparing code for release, focusing on stability and documentation.       | `develop`       | `main`         | `release/<version>`            | `git checkout develop && git checkout -b release/1.0.0`                            |
| `chore`           | Updates not related to feature development (e.g., CI/CD, documentation).  | Any             | Origin branch  | `chore/<task-name>`            | `git checkout develop && git checkout -b chore/update-dependencies`                |
| `experiment`      | Temporary branches for experimenting with new ideas or technologies.       | Any             | None (optional)| `experiment/<experiment-name>` | `git checkout develop && git checkout -b experiment/test-new-api`                  |

---

## **Workflow**
1. **Fork the repository** (if external contributor).
2. **Create a branch** according to the branching strategy.
3. **Make your changes**.
4. **Write meaningful commit messages**:
   - Format: `[<type>] <scope>: <description>`
   - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
   - Example: `[feat] authentication: add JWT support`.

5. **Push your branch** to the remote repository:
   ```bash
   git push origin <branch-name>
   ```