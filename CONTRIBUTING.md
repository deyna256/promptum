# Contributing to Promptum

Thank you for your interest in contributing to Promptum! We welcome contributions from the community.

## Getting Started

1. **Fork the repository** to your own GitHub account
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/promptum.git
   cd promptum
   ```
3. **Set up the development environment**:
   ```bash
   just sync  # Install/sync dependencies
   ```

## Making Changes

### Branch Naming

Create a new branch named after the issue number you're working on:

```bash
git checkout -b 42  # For issue #42
```

### One PR = One Issue

Each pull request should address exactly one issue. If you want to work on multiple issues, create separate branches and PRs for each.

### Work in Progress

If your PR is not ready for review, add `[WIP]` to the title:

```
[WIP] #42: Fix retry logic in OpenRouterClient
```

Remove `[WIP]` when the PR is ready for review.

## Submitting Changes

1. **Run tests and linting** before committing:
   ```bash
   just lint       # Lint and auto-fix
   just typecheck  # Type check
   just test       # Run tests
   ```

2. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "#42: Fix retry logic in OpenRouterClient"
   ```

3. **Push to your fork**:
   ```bash
   git push origin 42
   ```

4. **Create a Pull Request** from your fork to the main repository

5. **Tag the maintainer** (@deyna256) in a comment when your PR is ready for review

## CI Requirements

Pull requests must pass all CI checks before review. The maintainer will not review PRs with failing checks.

CI runs:
- Linting
- Type checking
- Tests

## Questions?

Feel free to ask questions in the issue comments or open a discussion.

Thank you for contributing!
