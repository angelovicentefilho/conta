"""
Testes de integração para endpoints de contas financeiras.

Testa todos os endpoints REST de CRUD para contas, com autenticação,
validações e tratamento de erros.
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


@pytest.fixture
def valid_user_payload():
    """Fixture para dados válidos de usuário."""
    return {
        "name": "João Silva",
        "email": "joao@example.com",
        "password": "MinhaSenh@123"
    }


@pytest.fixture
def valid_account_payload():
    """Fixture para dados válidos de conta."""
    return {
        "name": "Conta Corrente Principal",
        "type": "checking",
        "balance": 1000.0,
        "is_primary": True
    }


@pytest.fixture
def savings_account_payload():
    """Fixture para dados de conta poupança."""
    return {
        "name": "Poupança",
        "type": "savings",
        "balance": 500.0,
        "is_primary": False
    }


@pytest.fixture
def credit_card_payload():
    """Fixture para dados de cartão de crédito."""
    return {
        "name": "Cartão Visa",
        "type": "credit_card",
        "balance": -200.0,
        "is_primary": False
    }


class TestAccountCreation:
    """Testes para criação de contas."""
    
    def test_create_account_success(
        self, valid_user_payload, valid_account_payload
    ):
        """Deve criar conta com sucesso para usuário autenticado."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Criar conta
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/accounts/",
            json=valid_account_payload,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Conta Corrente Principal"
        assert data["type"] == "checking"
        assert float(data["balance"]) == 1000.0
        assert data["is_primary"] is True
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_account_unauthorized(self, valid_account_payload):
        """Deve falhar ao criar conta sem autenticação."""
        response = client.post("/api/v1/accounts/", json=valid_account_payload)
        assert response.status_code == 403
    
    def test_create_account_invalid_type(self, valid_user_payload):
        """Deve falhar com tipo de conta inválido."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Tentar criar conta com tipo inválido
        invalid_payload = {
            "name": "Conta Inválida",
            "type": "invalid_type",
            "balance": 100.0
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/accounts/",
            json=invalid_payload,
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_credit_card_negative_balance(
        self, valid_user_payload, credit_card_payload
    ):
        """Deve permitir saldo negativo para cartão de crédito."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Criar cartão com saldo negativo
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/accounts/",
            json=credit_card_payload,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "credit_card"
        assert float(data["balance"]) == -200.0
    
    def test_create_account_negative_balance_invalid(self, valid_user_payload):
        """Deve falhar com saldo negativo para conta que não permite."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Tentar criar conta corrente com saldo negativo
        invalid_payload = {
            "name": "Conta Corrente",
            "type": "checking",
            "balance": -100.0
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/accounts/",
            json=invalid_payload,
            headers=headers
        )
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()


class TestAccountListing:
    """Testes para listagem de contas."""
    
    def test_list_accounts_empty(self, valid_user_payload):
        """Deve retornar lista vazia para usuário sem contas."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Listar contas
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/accounts/", headers=headers)
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_accounts_with_data(
        self, valid_user_payload, valid_account_payload,
        savings_account_payload
    ):
        """Deve listar contas do usuário ordenadas."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Criar duas contas
        client.post(
            "/api/v1/accounts/", json=valid_account_payload, headers=headers
        )
        client.post(
            "/api/v1/accounts/", json=savings_account_payload, headers=headers
        )
        
        # Listar contas
        response = client.get("/api/v1/accounts/", headers=headers)
        
        assert response.status_code == 200
        accounts = response.json()
        assert len(accounts) == 2
        
        # Verificar estrutura dos dados
        account = accounts[0]
        assert "id" in account
        assert "name" in account
        assert "type" in account
        assert "balance" in account
        assert "is_primary" in account
        
        # Conta principal deve vir primeiro
        primary_accounts = [acc for acc in accounts if acc["is_primary"]]
        assert len(primary_accounts) == 1
        assert accounts[0]["is_primary"] is True
    
    def test_list_accounts_unauthorized(self):
        """Deve falhar ao listar contas sem autenticação."""
        response = client.get("/api/v1/accounts/")
        assert response.status_code == 403


class TestAccountRetrieval:
    """Testes para busca de conta específica."""
    
    def test_get_account_success(
        self, valid_user_payload, valid_account_payload
    ):
        """Deve buscar conta específica com sucesso."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Criar conta
        create_response = client.post(
            "/api/v1/accounts/",
            json=valid_account_payload,
            headers=headers
        )
        account_id = create_response.json()["id"]
        
        # Buscar conta
        response = client.get(
            f"/api/v1/accounts/{account_id}", headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["name"] == "Conta Corrente Principal"
        assert "created_at" in data
        assert "updated_at" in data
        assert "is_active" in data
    
    def test_get_account_not_found(self, valid_user_payload):
        """Deve falhar ao buscar conta inexistente."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Buscar conta inexistente
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/accounts/{fake_id}", headers=headers)
        
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()
    
    def test_get_account_unauthorized(self):
        """Deve falhar ao buscar conta sem autenticação."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/accounts/{fake_id}")
        assert response.status_code == 403


class TestAccountUpdate:
    """Testes para atualização de contas."""
    
    def test_update_account_name(
        self, valid_user_payload, valid_account_payload
    ):
        """Deve atualizar nome da conta."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Criar conta
        create_response = client.post(
            "/api/v1/accounts/",
            json=valid_account_payload,
            headers=headers
        )
        account_id = create_response.json()["id"]
        
        # Atualizar nome
        update_data = {"name": "Novo Nome da Conta"}
        response = client.put(
            f"/api/v1/accounts/{account_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Novo Nome da Conta"
        assert data["id"] == account_id
    
    def test_update_account_balance(
        self, valid_user_payload, valid_account_payload
    ):
        """Deve atualizar saldo da conta."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Criar conta
        create_response = client.post(
            "/api/v1/accounts/",
            json=valid_account_payload,
            headers=headers
        )
        account_id = create_response.json()["id"]
        
        # Atualizar saldo
        update_data = {"balance": 2500.75}
        response = client.put(
            f"/api/v1/accounts/{account_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert float(data["balance"]) == 2500.75
    
    def test_update_account_not_found(self, valid_user_payload):
        """Deve falhar ao atualizar conta inexistente."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tentar atualizar conta inexistente
        fake_id = str(uuid4())
        update_data = {"name": "Novo Nome"}
        response = client.put(
            f"/api/v1/accounts/{fake_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 404


class TestAccountDeletion:
    """Testes para exclusão de contas."""
    
    def test_delete_account_success(
        self, valid_user_payload, valid_account_payload,
        savings_account_payload
    ):
        """Deve deletar conta quando há múltiplas contas."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Criar duas contas
        client.post(
            "/api/v1/accounts/", json=valid_account_payload, headers=headers
        )
        create2 = client.post(
            "/api/v1/accounts/", json=savings_account_payload, headers=headers
        )
        account_id = create2.json()["id"]
        
        # Deletar segunda conta
        response = client.delete(
            f"/api/v1/accounts/{account_id}", headers=headers
        )
        
        assert response.status_code == 204
        
        # Verificar que conta foi removida
        get_response = client.get(
            f"/api/v1/accounts/{account_id}", headers=headers
        )
        assert get_response.status_code == 404
    
    def test_delete_account_not_found(self, valid_user_payload):
        """Deve falhar ao deletar conta inexistente."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tentar deletar conta inexistente
        fake_id = str(uuid4())
        response = client.delete(
            f"/api/v1/accounts/{fake_id}", headers=headers
        )
        
        assert response.status_code == 404


class TestPrimaryAccount:
    """Testes para gestão de conta principal."""
    
    def test_set_primary_account(
        self, valid_user_payload, valid_account_payload,
        savings_account_payload
    ):
        """Deve definir conta como principal."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Criar duas contas
        client.post(
            "/api/v1/accounts/", json=valid_account_payload, headers=headers
        )
        create2 = client.post(
            "/api/v1/accounts/", json=savings_account_payload, headers=headers
        )
        account_id = create2.json()["id"]
        
        # Definir segunda conta como principal
        response = client.patch(
            f"/api/v1/accounts/{account_id}/set-primary",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_primary"] is True
        assert data["id"] == account_id
    
    def test_set_primary_account_not_found(self, valid_user_payload):
        """Deve falhar ao definir conta inexistente como principal."""
        # Registrar e fazer login
        client.post("/auth/register", json=valid_user_payload)
        login_data = {
            "email": valid_user_payload["email"],
            "password": valid_user_payload["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tentar definir conta inexistente como principal
        fake_id = str(uuid4())
        response = client.patch(
            f"/api/v1/accounts/{fake_id}/set-primary",
            headers=headers
        )
        
        assert response.status_code == 404
