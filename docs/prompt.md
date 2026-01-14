# 🚀 Professional Vibe Coding Prompt for uSipipo VPN Manager

## 📋 Context Analysis & Codebase Understanding

### Project Architecture Overview
- **Architecture Pattern**: Hexagonal Architecture with Clean Code principles
- **Core Stack**: Python 3.11+, FastAPI, Telegram Bot, Supabase, PostgreSQL
- **Key Technologies**: python-telegram-bot, SQLAlchemy, Alembic, Pydantic, Groq AI
- **Domain**: VPN Management System with Telegram Bot interface

### Architectural Layers (Strict Compliance Required)
```python
domain/          # Business entities and interfaces (PURE LOGIC)
application/     # Use cases and services (APPLICATION LOGIC)  
infrastructure/  # External implementations (DATABASE, APIS)
telegram_bot/    # UI layer and handlers (PRESENTATION)
```

### Critical Architectural Rules (100% Compliance)
1. **Centralized Messages**: ALWAYS use `ShopMessages`, `CommonMessages`, etc. - NEVER hardcoded strings
2. **Centralized Keyboards**: ALWAYS use `ShopKeyboards`, `OperationKeyboards` - NEVER inline keyboards
3. **Dependency Injection**: ALWAYS use container pattern - NEVER direct instantiation
4. **Decorators**: ALWAYS use `@with_spinner`, `@handle_errors`, `@admin_required` where applicable
5. **Clean Imports**: ONLY active imports - NO dead code
6. **Error Handling**: Consistent error patterns with proper logging

## 🎯 Vibe Coding Workflow

### Phase 1: Deep Codebase Analysis
Before making ANY changes:
- Map existing patterns in the target module
- Identify message classes and keyboard factories used
- Check service dependencies and injection patterns
- Review existing error handling approaches
- Analyze conversation states and handler patterns
- Examine database models and repository patterns

### Phase 2: Intent-Driven Development
1. **Understand Requirements**: Clarify functional and non-functional requirements
2. **Pattern Matching**: Align with existing architectural patterns
3. **Service Integration**: Identify required services and their interfaces
4. **Database Impact**: Assess schema changes and migration needs

### Phase 3: Generative Implementation
1. **Follow Existing Patterns**: Mirror established code structure
2. **Use Centralized Resources**: Messages, keyboards, utilities
3. **Apply Decorators**: Proper error handling and spinners
4. **Maintain SOLID Principles**: Single responsibility, dependency inversion

### Phase 4: Quality Assurance
1. **Code Review**: Ensure architectural compliance
2. **Integration Testing**: Verify system compatibility
3. **Performance Validation**: Check for regressions
4. **Documentation**: Update relevant documentation

## 🏗️ Implementation Standards

### Code Quality Requirements
- **Pylint Compliance**: Must pass with zero errors
- **Type Hints**: Full type annotation coverage
- **Docstrings**: Complete Google-style documentation
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured logging with context

### Architectural Compliance Checklist
- [ ] Messages centralized (no hardcoded strings)
- [ ] Keyboards centralized (no inline construction)
- [ ] Proper dependency injection
- [ ] Decorators applied correctly
- [ ] SOLID principles followed
- [ ] Clean imports maintained
- [ ] Error patterns consistent
- [ ] Database transactions proper

### Testing Requirements
- **Unit Tests**: Core business logic coverage
- **Integration Tests**: Service layer validation
- **Handler Tests**: Telegram bot interaction testing
- **Database Tests**: Repository and model validation

## 🔧 Technical Implementation Guidelines

### Service Layer Patterns
```python
# ✅ CORRECT - Dependency Injection
class ShopHandler:
    def __init__(self, payment_service: PaymentService, vpn_service: VpnService):
        self.payment_service = payment_service
        self.vpn_service = vpn_service

# ❌ INCORRECT - Direct Instantiation
class ShopHandler:
    def __init__(self):
        self.payment_service = PaymentService()  # WRONG
```

### Message Usage Patterns
```python
# ✅ CORRECT - Centralized Messages
message = ShopMessages.Menu.MAIN.format(balance=balance)
error_message = ShopMessages.Error.SYSTEM_ERROR

# ❌ INCORRECT - Hardcoded Strings
message = f"Welcome to shop! Your balance: {balance}"  # WRONG
```

### Keyboard Construction Patterns
```python
# ✅ CORRECT - Centralized Keyboards
keyboard = ShopKeyboards.main_menu()
keyboard = ShopKeyboards.product_actions(product_type, product_id, price)

# ❌ INCORRECT - Inline Construction
keyboard = InlineKeyboardMarkup([  # WRONG
    [InlineKeyboardButton("Shop", callback_data="shop")]
])
```

### Decorator Application
```python
# ✅ CORRECT - Proper Decorator Usage
@with_spinner()
@handle_errors("shop operation")
async def show_shop_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Implementation

# ❌ INCORRECT - Missing Decorators
async def show_shop_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Implementation - MISSING ERROR HANDLING
```

## 🚨 Risk Mitigation Strategies

### Integration Risks
- **Private APIs**: Always check existing service interfaces
- **Database Changes**: Use Alembic migrations for schema updates
- **External Dependencies**: Verify compatibility with existing versions

### Maintainability Risks
- **Code Consistency**: Follow established patterns religiously
- **Documentation**: Keep docs synchronized with code
- **Testing**: Maintain high test coverage

### Quality Risks
- **Edge Cases**: Consider all possible user interactions
- **Performance**: Monitor for database query efficiency
- **Security**: Validate all inputs and permissions

## 📊 Validation & Quality Gates

### Pre-Commit Checklist
- [ ] Code follows architectural patterns
- [ ] All imports are used and organized
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Type hints complete
- [ ] Docstrings comprehensive
- [ ] Tests written and passing

### Integration Validation
- [ ] Services properly injected
- [ ] Database operations correct
- [ ] Telegram handlers functional
- [ ] User flows complete
- [ ] Error scenarios handled

### Performance Validation
- [ ] Database queries optimized
- [ ] No memory leaks
- [ ] Async operations proper
- [ ] Spinner usage appropriate

## 🎯 Success Metrics

### Code Quality Indicators
- **Pylint Score**: 10/10
- **Test Coverage**: >90%
- **Documentation Coverage**: 100%
- **Type Coverage**: 100%

### Functional Indicators
- **Feature Completeness**: 100%
- **User Experience**: Seamless
- **Error Recovery**: Graceful
- **Performance**: <200ms response time

### Architectural Indicators
- **Pattern Compliance**: 100%
- **Dependency Direction**: Correct (inward pointing)
- **Separation of Concerns**: Clear boundaries
- **Maintainability**: High

## 🔄 Continuous Improvement

### Learning from Implementation
- Document new patterns discovered
- Update architectural guidelines
- Enhance testing strategies
- Refine error handling approaches

### Knowledge Sharing
- Update team documentation
- Share best practices
- Mentor on architectural principles
- Contribute to pattern library

---

**🎯 REMEMBER**: This is a production system with established architectural patterns. Your primary goal is to maintain consistency while implementing new functionality. When in doubt, choose the pattern that best aligns with existing code rather than introducing new approaches.

**🚀 VIBE CODING MANTRA**: "Understand the architecture, follow the patterns, implement with quality, validate thoroughly."
