#!/usr/bin/env python3
"""
Script de teste para a API de upload de arquivos
"""
import sys
from io import BytesIO

import requests

API_BASE_URL = "http://localhost/api/admin"


def create_test_file(filename, content):
    """Cria um arquivo de teste"""
    return BytesIO(content.encode("utf-8"))


def test_upload_text_file():
    """Teste de upload de arquivo TXT"""
    print("\n=== Teste 1: Upload de arquivo TXT ===")

    # Criar arquivo de teste
    file_content = "Este é um arquivo de teste para o sistema TACA.\nConteúdo de teste."
    files = {
        "file": ("teste.txt", create_test_file("teste.txt", file_content), "text/plain")
    }
    data = {"bucket": "documentos-teste"}

    response = requests.post(f"{API_BASE_URL}/files/upload", files=files, data=data)

    if response.status_code == 201:
        result = response.json()
        print("✅ Upload realizado com sucesso!")
        print(f"   Hash: {result['file_hash']}")
        print(f"   URL Pública: {result['public_url']}")
        print(f"   Bucket: {result['bucket']}")
        print(f"   Tamanho: {result['size']} bytes")
        return result
    else:
        print(f"❌ Erro no upload: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_upload_pdf_simulation():
    """Teste de upload simulando um PDF"""
    print("\n=== Teste 2: Upload simulando PDF ===")

    # Simular conteúdo de PDF (em produção seria um arquivo real)
    pdf_content = "%PDF-1.4\nFake PDF content for testing\n%%EOF"
    files = {
        "file": (
            "regulamento.pdf",
            BytesIO(pdf_content.encode("utf-8")),
            "application/pdf",
        )
    }
    data = {"bucket": "regulamentos"}

    response = requests.post(f"{API_BASE_URL}/files/upload", files=files, data=data)

    if response.status_code == 201:
        result = response.json()
        print("✅ Upload realizado com sucesso!")
        print(f"   Hash: {result['file_hash']}")
        print(f"   URL Pública: {result['public_url']}")
        print(f"   Object Name: {result['object_name']}")
        return result
    else:
        print(f"❌ Erro no upload: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_invalid_bucket():
    """Teste com nome de bucket inválido"""
    print("\n=== Teste 3: Bucket inválido (deve falhar) ===")

    file_content = "Teste"
    files = {"file": ("teste.txt", BytesIO(file_content.encode("utf-8")), "text/plain")}
    data = {"bucket": "AB"}  # Muito curto

    response = requests.post(f"{API_BASE_URL}/files/upload", files=files, data=data)

    if response.status_code == 400:
        print("✅ Validação funcionou corretamente!")
        print(f"   Erro esperado: {response.json()}")
    else:
        print(f"❌ Esperava erro 400, recebeu: {response.status_code}")


def test_delete_file(bucket, object_name):
    """Teste de deleção de arquivo"""
    print("\n=== Teste 4: Deletar arquivo ===")

    data = {"bucket": bucket, "object_name": object_name}

    response = requests.delete(f"{API_BASE_URL}/files/delete", json=data)

    if response.status_code == 204:
        print("✅ Arquivo deletado com sucesso!")
    else:
        print(f"❌ Erro ao deletar: {response.status_code}")
        print(f"   {response.text}")


def test_multiple_buckets():
    """Teste de upload em múltiplos buckets"""
    print("\n=== Teste 5: Upload em diferentes buckets ===")

    buckets = ["fotos", "documentos", "relatorios"]

    for bucket in buckets:
        file_content = f"Conteúdo de teste para bucket {bucket}"
        files = {
            "file": (
                f"arquivo_{bucket}.txt",
                BytesIO(file_content.encode("utf-8")),
                "text/plain",
            )
        }
        data = {"bucket": bucket}

        response = requests.post(f"{API_BASE_URL}/files/upload", files=files, data=data)

        if response.status_code == 201:
            result = response.json()
            print(f"✅ Bucket '{bucket}': Upload OK - {result['public_url']}")
        else:
            print(f"❌ Bucket '{bucket}': Erro {response.status_code}")


def main():
    print("=" * 60)
    print("TESTE DA API DE UPLOAD DE ARQUIVOS - MinIO Integration")
    print("=" * 60)

    try:
        # Teste 1: Upload TXT
        result1 = test_upload_text_file()

        # Teste 2: Upload PDF
        result2 = test_upload_pdf_simulation()

        if result2:
            pass

        # Teste 3: Validação de bucket
        test_invalid_bucket()

        # Teste 4: Deleção (se upload 1 funcionou)
        if result1:
            test_delete_file(result1["bucket"], result1["object_name"])

        # Teste 5: Múltiplos buckets
        test_multiple_buckets()

        print("\n" + "=" * 60)
        print("TESTES CONCLUÍDOS!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API.")
        print("   Verifique se o docker-compose está rodando:")
        print("   docker-compose -f docker-compose.dev.yml up")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
