import json
import sys

# Importações locais do nosso próprio projeto modularizado
from mocks import get_mock_aws_data
from auditors import audit_ebs_volumes, audit_elastic_ips

try:
    import boto3
    from botocore.exceptions import NoCredentialsError, PartialCredentialsError
except ImportError:
    print("[!] Erro: Boto3 não encontrado. Ative o venv com 'source venv/bin/activate' e rode 'pip install boto3'")
    sys.exit(1)

if __name__ == "__main__":
    print("[*] Iniciando motor de auditoria Cloud Sentinel...")
    
    # INTERRUPTOR: True = Mock/Simulado | False = AWS Real
    MODO_MOCK = True
    
    relatorio_completo = []

    if MODO_MOCK:
        print("[!] Executando em MODO SIMULADO (Dados Sintéticos).")
        ebs_data, eip_data = get_mock_aws_data()
        relatorio_completo.extend(audit_ebs_volumes(ebs_data))
        relatorio_completo.extend(audit_elastic_ips(eip_data))
    else:
        print("[⚡] Conectando à AWS Real via Boto3...")
        try:
            ec2_client = boto3.client("ec2", region_name="us-east-1")
            
            real_ebs = ec2_client.describe_volumes()
            real_eip = ec2_client.describe_addresses()
            
            relatorio_completo.extend(audit_ebs_volumes(real_ebs))
            relatorio_completo.extend(audit_elastic_ips(real_eip))
            
        except (NoCredentialsError, PartialCredentialsError):
            print("[X] Erro de Autenticação: Nenhuma credencial AWS encontrada na WSL.")
            sys.exit(1)
        except Exception as e:
            print(f"[X] Erro inesperado ao conectar na AWS: {e}")
            sys.exit(1)
    
    print("\n[+] Relatório de Auditoria Consolidado (JSON Gerado):")
    print(json.dumps(relatorio_completo, indent=4, default=str))