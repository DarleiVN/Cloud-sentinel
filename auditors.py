import sqlite3
import csv
from datetime import datetime, timezone

def audit_ebs_volumes(ebs_data=None):
    """Recebe os dados de volumes e retorna o relatório de inativos."""
    return [
        {"Resource_Type": "EBS_Volume", "Resource_Id": "vol-9876543210fedcba0", "Details": "50GB (gp2) - Inativo há 15 dias", "Estimated_Monthly_Loss_USD": 5.0},
        {"Resource_Type": "EBS_Volume", "Resource_Id": "vol-aaaaabbbbbccccc11", "Details": "200GB (io2) - Inativo há 5 dias", "Estimated_Monthly_Loss_USD": 20.0},
        {"Resource_Type": "EBS_Volume", "Resource_Id": "vol-dddddeeeeefffff22", "Details": "80GB (gp3) - Inativo há 30 dias", "Estimated_Monthly_Loss_USD": 8.0}
    ]

def audit_elastic_ips(eip_data=None):
    """Recebe os dados de IPs e retorna o relatório de desassociados."""
    return [
        {"Resource_Type": "Elastic_IP", "Resource_Id": "34.200.15.99", "Details": "Desassociado da Instância", "Estimated_Monthly_Loss_USD": 3.6},
        {"Resource_Type": "Elastic_IP", "Resource_Id": "18.232.45.112", "Details": "Desassociado da Instância", "Estimated_Monthly_Loss_USD": 3.6}
    ]

def audit_ec2_right_sizing(ec2_data=None):
    """Recebe os dados de EC2 e retorna o relatório de superdimensionamento."""
    return [
        {"Resource_Type": "EC2_Instance_RightSizing", "Resource_Id": "i-1234567890abcdef0", "Details": "t3.medium | Média CPU 4.2%", "Estimated_Monthly_Loss_USD": 23.0},
        {"Resource_Type": "EC2_Instance_RightSizing", "Resource_Id": "i-aaaa1111bbbb2222c", "Details": "m5.xlarge | Média CPU 1.8%", "Estimated_Monthly_Loss_USD": 74.5},
        {"Resource_Type": "EC2_Instance_RightSizing", "Resource_Id": "i-cccc3333dddd4444e", "Details": "t3.micro | Média CPU 8.9%", "Estimated_Monthly_Loss_USD": 8.4}
    ]

# --- ADICIONANDO NOVOS REGISTROS DE AUDITORIA ---

def audit_rds_databases(rds_data=None):
    """Simula a auditoria de bancos de dados RDS ligados sem conexões ativas."""
    return [
        {"Resource_Type": "RDS_Database_Idle", "Resource_Id": "rds-prod-postgres-replica", "Details": "db.m5.large | 0 conexões em 7 dias", "Estimated_Monthly_Loss_USD": 115.0},
        {"Resource_Type": "RDS_Database_Idle", "Resource_Id": "rds-dev-mysql", "Details": "db.t3.medium | Idle há 14 dias", "Estimated_Monthly_Loss_USD": 32.0}
    ]

def audit_s3_buckets(s3_data=None):
    """Simula a auditoria de buckets S3 sem uso ou acumulando lixo."""
    return [
        {"Resource_Type": "S3_Bucket_Unused", "Resource_Id": "company-backup-old-temp", "Details": "Armazenamento Standard | 1.2TB sem leitura", "Estimated_Monthly_Loss_USD": 27.6},
        {"Resource_Type": "S3_Bucket_Unused", "Resource_Id": "staging-logs-archive", "Details": "Objetos expirados sem Lifecycle Policy", "Estimated_Monthly_Loss_USD": 14.2}
    ]

# --- FUNÇÕES DE INFRAESTRUTURA (CSV E BANCO) ---

def export_to_csv(relatorio, filename="relatorio_finops.csv"):
    """Exporta o relatório consolidado para um arquivo CSV."""
    if not relatorio:
        print("[!] Relatório vazio. Nada para exportar para CSV.")
        return
    campos = relatorio[0].keys()
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(relatorio)
        print(f"[🟢] Sucesso! Relatório financeiro exportado para: {filename}")
    except Exception as e:
        print(f"[X] Erro ao exportar para CSV: {e}")

def save_to_database(relatorio, db_path="/var/lib/grafana/cloud_sentinel.db"):
    """Grava o relatório dinamicamente no banco de dados SQLite do Grafana."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria_custos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                estimated_loss REAL
            )
        """)
        
        timestamp_atual = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        for item in relatorio:
            cursor.execute("""
                INSERT INTO auditoria_custos (timestamp, resource_type, resource_id, details, estimated_loss)
                VALUES (?, ?, ?, ?, ?)
            """, (
                timestamp_atual,
                item.get("Resource_Type"),
                item.get("Resource_Id"),
                item.get("Details"),
                float(item.get("Estimated_Monthly_Loss_USD", 0.0))
            ))
            
        conn.commit()
        print(f"[🟢] Sucesso! {len(relatorio)} registros persistidos no banco de dados: {db_path}")
        
    except sqlite3.Error as e:
        print(f"[X] Erro ao salvar no banco de dados: {e}")
    finally:
        if conn:
            conn.close()