import csv
import sqlite3
from datetime import datetime, timezone

def audit_ebs_volumes(data):
    """Filtra volumes EBS ociosos (status 'available')."""
    idle_volumes = []
    for volume in data.get("Volumes", []):
        if volume.get("State") == "available":
            vol_id = volume["VolumeId"]
            size = volume["Size"]
            create_time = volume["CreateTime"]
            days_idle = (datetime.now(timezone.utc) - create_time).days
            estimated_monthly_loss = size * 0.10
            
            idle_volumes.append({
                "Resource_Type": "EBS_Volume",
                "Resource_Id": vol_id,
                "Details": f"{size}GB ({volume['VolumeType']})",
                "Days_Idle": days_idle,
                "Estimated_Monthly_Loss_USD": round(estimated_monthly_loss, 2)
            })
    return idle_volumes

def audit_elastic_ips(data):
    """Identifica Elastic IPs alocados e não associados."""
    idle_eips = []
    for address in data.get("Addresses", []):
        if "InstanceId" not in address:
            public_ip = address["PublicIp"]
            alloc_id = address["AllocationId"]
            idle_eips.append({
                "Resource_Type": "Elastic_IP",
                "Resource_Id": public_ip,
                "Details": f"Allocation ID: {alloc_id}",
                "Days_Idle": "N/A",
                "Estimated_Monthly_Loss_USD": 3.60
            })
    return idle_eips

def audit_ec2_right_sizing(data):
    """Identifica instâncias EC2 ligadas com uso de CPU abaixo de 10%."""
    underutilized_instances = []
    for reservation in data.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            state = instance.get("State", {}).get("Name")
            cpu_usage = instance.get("CpuUtilizationAverage", 100.0)
            
            if state == "running" and cpu_usage < 10.0:
                instance_id = instance["InstanceId"]
                instance_type = instance["InstanceType"]
                estimated_savings = 23.00 
                
                underutilized_instances.append({
                    "Resource_Type": "EC2_Instance_RightSizing",
                    "Resource_Id": instance_id,
                    "Details": f"Type: {instance_type} | Avg CPU: {cpu_usage}%",
                    "Days_Idle": "N/A",
                    "Estimated_Monthly_Loss_USD": round(estimated_savings, 2)
                })
    return underutilized_instances

def export_to_csv(relatorio, filename="relatorio_finops.csv"):
    """Exporta o relatório consolidado para um arquivo CSV estruturado."""
    if not relatorio:
        print("[!] Relatório vazio. Nenhum arquivo CSV gerado.")
        return

    headers = ["Resource_Type", "Resource_Id", "Details", "Days_Idle", "Estimated_Monthly_Loss_USD"]

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(relatorio)
        print(f"[🟢] Sucesso! Relatório financeiro exportado para: {filename}")
    except Exception as e:
        print(f"[X] Erro ao exportar para CSV: {e}")


def save_to_database(relatorio, db_name="cloud_sentinel.db"):
    """Cria a tabela se não existir e insere os registros com timestamp atual."""
    if not relatorio:
        return

    # Captura o momento exato da varredura (Série Temporal)
    timestamp_atual = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Conecta ao arquivo de banco (se não existir, o SQLite cria na hora)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Cria a tabela estruturada para auditoria histórica
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria_custos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                days_idle TEXT,
                estimated_loss REAL
            )
        """)

        # Prepara a query de inserção em massa
        dados_para_inserir = []
        for item in relatorio:
            dados_para_inserir.append((
                timestamp_atual,
                item["Resource_Type"],
                item["Resource_Id"],
                item["Details"],
                str(item["Days_Idle"]),
                item["Estimated_Monthly_Loss_USD"]
            ))

        # Executa o insert de todas as linhas de uma vez só
        cursor.executemany("""
            INSERT INTO auditoria_custos (timestamp, resource_type, resource_id, details, days_idle, estimated_loss)
            VALUES (?, ?, ?, ?, ?, ?)
        """, dados_para_inserir)

        # Salva as alterações e fecha a conexão
        conn.commit()
        conn.close()
        print(f"[🟢] Sucesso! {len(relatorio)} registros persistidos no banco de dados: {db_name}")

    except Exception as e:
        print(f"[X] Erro ao salvar no banco de dados: {e}")