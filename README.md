# Doce Encanto

E-commerce acadêmico de cupcakes desenvolvido para o Projeto Integrador Transdisciplinar em Engenharia de Software II.

## Funcionalidades

- Cadastro, login e logout.
- Catálogo de cupcakes ativos.
- Carrinho em sessão com quantidades entre 1 e 20.
- Checkout com endereço e pagamento demonstrativo.
- Histórico e detalhes de pedidos protegidos por usuário.
- Administração de produtos e status de pedidos pelo Django Admin.

> O projeto não processa pagamentos reais. Todos os pedidos e dados são demonstrativos.

## Execução local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

No Linux ou macOS, ative o ambiente com `source .venv/bin/activate`.

A aplicação ficará disponível em `http://127.0.0.1:8000/` e o painel em `http://127.0.0.1:8000/admin/`.

## Testes

```powershell
python manage.py test
coverage run manage.py test
coverage report
```

## Variáveis de produção

| Variável | Finalidade |
|---|---|
| `SECRET_KEY` | Chave secreta do Django |
| `DEBUG` | Deve ser `False` em produção |
| `DATABASE_URL` | Conexão PostgreSQL |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula |
| `CSRF_TRUSTED_ORIGINS` | Origens HTTPS confiáveis |
| `ADMIN_USERNAME` | Administrador demonstrativo opcional |
| `ADMIN_PASSWORD` | Senha do administrador opcional |
| `ADMIN_EMAIL` | E-mail do administrador opcional |

## Publicação no Render

1. Faça fork ou conecte este repositório à sua conta Render.
2. Escolha **New Blueprint** e selecione o arquivo `render.yaml`.
3. Se desejar um administrador automático, adicione as três variáveis `ADMIN_*` como segredos.
4. Aguarde o build, as migrações e a carga do catálogo.

O plano gratuito do Render pode hibernar por inatividade e o banco PostgreSQL gratuito possui prazo limitado. Mantenha também a execução local disponível para a apresentação.

## Estrutura

- `shop/`: domínio, carrinho, formulários, views, administração e testes.
- `templates/`: interface HTML em português.
- `static/`: estilos e fotografias geradas para o projeto.
- `docs/`: documentação acadêmica e diagramas.

Autor: Matheus da Silva Mattos - RGM 36338770.
