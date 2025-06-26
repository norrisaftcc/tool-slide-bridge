# FLOW/SAFE Workflow Process

This document outlines our proven workflow process that combines FLOW (Follow Logical Work Order), SAFE (Scaled Agile Framework for Education), and VIBE (Verification Inspires Behavior Examples) methodologies.

## Core Principles

### FLOW: Follow Logical Work Order
- **Don't block on non-blockers**: Continue forward progress while reporting issues that can be addressed later
- **Parallel workflows**: Run reviews and testing simultaneously when possible
- **End run when needed**: Complete critical path work even if documentation/cleanup is pending
- **Report blockers**: Always communicate what's blocking progress vs what's just cleanup

### SAFE: Scaled Agile Framework for Education
- **Work within GitHub**: All development happens through issues and pull requests
- **Virtual environments**: Proper isolation and dependency management
- **Security first**: Use .gitignore to keep secrets and packages out of repo
- **Responsible development**: Follow established patterns and conventions

### VIBE: Verification Inspires Behavior Examples
- **Test-driven approach**: Write tests that demonstrate expected behavior
- **Example-driven documentation**: Show how things work, not just what they do
- **Verification checklists**: Use PR templates to ensure quality gates
- **Behavior validation**: Automated testing validates expected outcomes

## Workflow Process

### 1. Issue Creation Process

#### Issue Types and When to Use Them
- **Epic**: Large features spanning multiple PRs (e.g., "Implement hybrid MARP/python-pptx solution")
- **Feature**: Single deliverable functionality (e.g., "Add fortune-style rotating messages")
- **Bug**: Fix broken functionality (e.g., "MARP conversion fails on complex tables")
- **Tech Debt**: Improvement without new functionality (e.g., "Add proper test structure")

#### Issue Structure
```markdown
## Summary
Brief description of what needs to be done

## Background
Why this work is needed, context from previous work

## Acceptance Criteria
- [ ] Specific, testable requirements
- [ ] Each criterion should be verifiable
- [ ] Include both functional and non-functional requirements

## Success Metrics
How we'll know this is working correctly

## Labels
Appropriate labels for categorization and filtering
```

#### Labels We Use
- `epic`, `feature`, `bug`, `tech-debt`: Issue types
- `documentation`, `testing`, `security`: Work categories
- `flow`, `safe`, `vibe`: Process-related
- `marp`, `python-pptx`, `web`: Technical components

### 2. Branch Strategy

#### Branch Naming Conventions
- `feature/descriptive-name`: New functionality
- `bugfix/issue-description`: Bug fixes
- `hotfix/critical-fix`: Emergency fixes to main
- `docs/documentation-update`: Documentation-only changes

#### Branch Creation
```bash
# Start from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/issue-description

# Link to issue in first commit
git commit -m "Initial commit for #[issue-number]"
```

#### Parallel Development
- Multiple feature branches can be worked on simultaneously
- Use different branches for independent features
- Coordinate with team when branches might conflict

### 3. Development Workflow

#### Starting Work
1. **Select Issue**: Choose from backlog based on priority and dependencies
2. **Create Branch**: Follow naming conventions
3. **Initial Commit**: Link to issue number in commit message
4. **Plan Implementation**: Break down work into logical steps

#### Implementation Standards
- **Code Quality**: Follow existing patterns and conventions
- **Testing**: Write tests for new functionality
- **Documentation**: Update relevant docs as you go
- **Security**: Never commit secrets, use proper .gitignore patterns

#### FLOW in Practice: Example from Phase 1 Implementation
```
1. Created issue #1 for dev plan
2. Created PR #2 for infrastructure while planning Phase 1
3. Implemented Phase 1 MARP converter
4. Tested locally while creating PR #4
5. Reported non-blockers (test structure, output files) but didn't wait
6. Created PR for parallel review/testing
```

#### Quality Gates
Before committing:
- [ ] Code follows project conventions
- [ ] Tests pass (if test framework exists)
- [ ] Linting passes (run `npm run lint` or equivalent)
- [ ] Type checking passes (run `mypy` or equivalent)
- [ ] No secrets in code
- [ ] Documentation updated

### 4. Pull Request Process

#### PR Creation
```bash
# Push branch
git push -u origin feature/branch-name

# Create PR with template
gh pr create --title "Descriptive title referencing #issue" --body "$(cat <<'EOF'
## Summary
Brief description of changes

## Related Issue
Closes #[issue-number]

## Changes Made
- [ ] Specific change 1
- [ ] Specific change 2

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## VIBE Checklist
- [ ] Code follows existing patterns
- [ ] Tests demonstrate expected behavior
- [ ] Documentation includes examples
- [ ] Security considerations addressed

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

#### Review Process
1. **Self-review**: Check your own PR first
2. **Automated checks**: Ensure CI passes
3. **Parallel workflows**: Don't wait for review to start testing
4. **Address feedback**: Make requested changes promptly
5. **Merge when ready**: Use appropriate merge strategy

#### FLOW Principle: Parallel Review and Testing
- Create PR immediately when ready for review
- Start local testing while reviews are happening
- Continue development on next feature if this one is waiting
- Report any blockers but don't wait for non-critical feedback

### 5. Testing Strategy

#### Test Types
- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Manual Tests**: Verify user experience

#### Testing Workflow
```bash
# Run all tests
npm test

# Run specific test types
npm run test:unit
npm run test:integration

# Check MARP functionality
npm run test:marp
```

#### VIBE Testing Approach
- Write tests that show how the feature should behave
- Include examples in test names: `test_converts_claude_markdown_to_corporate_theme`
- Test both happy path and error conditions
- Use descriptive assertions that explain expected behavior

### 6. Merge and Release Process

#### Merge Criteria
- [ ] All automated checks pass
- [ ] At least one code review approval
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] No merge conflicts

#### Merge Strategies
- **Squash and merge**: For feature branches (keeps clean history)
- **Merge commit**: For releases or major milestones
- **Rebase**: For simple changes that don't need merge commit

#### Post-Merge Cleanup
```bash
# After successful merge
git checkout main
git pull origin main
git branch -d feature/branch-name  # Delete local branch
git push origin --delete feature/branch-name  # Delete remote branch
```

## Non-Blocker Management

### What Qualifies as a Non-Blocker
- Documentation improvements that don't affect functionality
- Code cleanup that doesn't fix bugs
- Test structure improvements
- Performance optimizations
- Style/formatting issues

### How to Handle Non-Blockers
1. **Report them**: Create issues or add to existing ones
2. **Don't wait**: Continue with critical path work
3. **Address later**: Schedule in next iteration or as tech debt
4. **Communicate**: Make sure team knows what's deferred

### Example Non-Blockers from Our Work
- Need to add proper tests directory structure to Phase 1 PR
- Some generated output files included (should be in .gitignore)
- Could optimize CLI help text and error messages
- Documentation could be expanded with more examples

## Communication Patterns

### Status Updates
- Use PR comments for progress updates
- Link related issues and PRs
- Tag team members when input is needed
- Update issue status as work progresses

### Escalation Process
1. **Technical blockers**: Comment on PR/issue, tag maintainer
2. **Process questions**: Reference this document or ask in issue
3. **Urgent issues**: Use Slack/direct communication + GitHub issue
4. **Dependencies**: Clearly document what you're waiting for

## Tools and Commands

### Essential Git Commands
```bash
# Start new work
git checkout main && git pull origin main
git checkout -b feature/new-feature

# Regular development
git add . && git commit -m "Descriptive commit message"
git push -u origin feature/new-feature

# Create PR
gh pr create --title "Title" --body "Description"

# Update branch with main
git checkout main && git pull origin main
git checkout feature/branch && git merge main
```

### Quality Commands
```bash
# Python quality checks
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/

# Node.js quality checks
npm run lint
npm run format

# Testing
python -m pytest
npm test
```

### Project Setup Commands
```bash
# Initial setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
npm install

# MARP setup
npm run install-marp
npm run test:marp
```

## Success Patterns We've Established

### What Works Well
1. **Issue-driven development**: Every change starts with an issue
2. **Parallel workflows**: Reviews happen while testing continues
3. **Non-blocker reporting**: Document issues but don't wait
4. **Quality gates**: Automated checks catch problems early
5. **Template usage**: Consistent PR and issue templates

### Lessons Learned
1. **Plan first**: User interruption taught us to plan before implementing
2. **Test early**: MARP installation issues caught early in testing
3. **Git workflow**: Cherry-pick conflicts resolved by using direct file copies
4. **Communication**: Clear status updates prevent confusion

### Metrics for Success
- **Velocity**: How quickly we move from issue to merged PR
- **Quality**: Automated checks pass rate, bug reports
- **Flow**: Time spent blocked vs time spent on value-add work
- **Collaboration**: How well parallel workflows coordinate

## Future Improvements

### Process Improvements
- Automated issue creation from templates
- Better integration between local testing and CI
- More granular labeling system
- Automated dependency detection

### Tooling Improvements
- Pre-commit hooks for quality checks
- Automated changelog generation
- Better test reporting and coverage tracking
- Integration with project management tools

---

This document is living and should be updated as our process evolves. When you notice something that works well or could be improved, update this documentation.