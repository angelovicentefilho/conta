# Diretrizes de Código e Boas Práticas

## Tamanho de Classes

Com base nas melhores práticas de Clean Code e desenvolvimento em Python:

### Classes de Produção
- **Máximo recomendado**: 200 linhas
- **Máximo aceitável**: 300 linhas  
- **Responsabilidade única**: Cada classe deve ter apenas uma razão para mudar

### Classes de Teste
- **Máximo recomendado**: 300 linhas
- **Máximo aceitável**: 400 linhas
- **Organização**: Agrupar testes por funcionalidade relacionada

## Estado Atual dos Arquivos de Teste

### Arquivos que excedem as diretrizes:

1. **tests/integration/test_account_endpoints.py** - 529 linhas
   - ✅ **Status**: OK - Bem estruturado com 6 classes pequenas (60-120 linhas cada)
   - Classes: TestAccountCreation, TestAccountListing, TestAccountRetrieval, TestAccountUpdate, TestAccountDeletion, TestPrimaryAccount

2. **tests/unit/test_transaction_service.py** - 438 linhas  
   - ⚠️ **Status**: ATENÇÃO - TestTransactionService muito grande (~295 linhas)
   - Classes: TestTransactionService (295 linhas), TestCategoryService (112 linhas)
   - **Sugestão**: Dividir TestTransactionService em classes menores por funcionalidade

3. **tests/unit/test_dashboard_service.py** - 405 linhas
   - ✅ **Status**: OK - Bem estruturado com 3 classes organizadas
   - Classes: TestDashboardService, TestFinancialAnalyticsService, TestDashboardEdgeCases

4. **tests/integration/test_dashboard_controller.py** - 404 linhas
   - ✅ **Status**: OK - Bem estruturado com 3 classes organizadas  
   - Classes: TestDashboardControllers, TestDashboardValidation, TestDashboardPerformance

## Recomendações de Refatoração

### Para test_transaction_service.py:

A classe `TestTransactionService` poderia ser dividida em:

```python
class TestTransactionCreation:
    """Testes para criação de transações"""
    # test_create_transaction_success
    # test_create_recurring_transaction  
    # test_create_transaction_account_not_found
    # test_create_transaction_category_not_found

class TestTransactionRetrieval:
    """Testes para busca de transações"""
    # test_get_user_transactions

class TestTransactionDeletion:
    """Testes para exclusão de transações"""
    # test_delete_transaction
```

### Princípios Aplicados:

1. **Single Responsibility**: Cada classe de teste tem uma responsabilidade específica
2. **DRY (Don't Repeat Yourself)**: Fixtures compartilhadas no conftest.py
3. **Readability**: Nomes claros e organização lógica
4. **Maintainability**: Fácil localização e modificação de testes

## Ferramentas de Qualidade de Código

As seguintes ferramentas estão configuradas no projeto:

- **Black**: Formatação automática (linha máxima: 88 caracteres)
- **isort**: Organização de imports
- **flake8**: Linting e detecção de problemas
- **mypy**: Verificação de tipos
- **pytest**: Framework de testes com coverage

## Métricas de Qualidade

### Cobertura de Testes
- **Meta**: >90% de cobertura
- **Comando**: `make test-coverage`

### Complexidade
- **Meta**: Complexidade ciclomática <10 por método
- **Ferramenta**: radon (a ser adicionada)

## Próximos Passos

1. Refatorar `TestTransactionService` em classes menores
2. Adicionar ferramenta de complexidade (radon)
3. Configurar limites automáticos no CI/CD
4. Documentar padrões específicos de fixtures
