

# python-aes


This is my simple implementation of the AES256 algorithm.
I initially implemented this project originally as part of the
Cryptography Course at the Högskolan Dalarna in 2015.
The concept of each function can be found on Wikipedia.

Although it can be used in practice, it's main purpose was
 to learn the algorithm and practice my python. For better performance
consider C/C++ implementations.


`AESInterface` defines a minimum set of functions which an AES algorithm should
have. There are

- `AESString` (implementing CBC)
- `AESBytes` (implementing CBC for file encryption)
- `AESStringCTR` (implementing Counter-Mode)
- `AESBytesCTR`(implementing Counter-Mode for file encryption)

For usage of the classes have a look at the tests.

## Release Process

This project uses [Commitizen](https://commitizen-tools.github.io/) for automated versioning based on [Conventional Commits](https://www.conventionalcommits.org/).

### Conventional Commit Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature (bumps minor version)
- `fix` - Bug fix (bumps patch version)
- `docs` - Documentation only
- `style` - Code style changes
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `test` - Test changes
- `chore` - Maintenance
- `build` - Build system changes
- `ci` - CI/CD changes
- `revert` - Revert previous commit

### Release Workflow
1. Create a PR with conventional commits
2. On merge to `main`, the version is automatically bumped
3. An annotated tag (e.g., `v0.1.0`) is created
