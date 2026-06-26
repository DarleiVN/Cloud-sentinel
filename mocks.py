from datetime import datetime, timezone, timedelta

def get_mock_aws_data():
    """Simula uma infraestrutura corporativa robusta com múltiplos recursos para teste de FinOps."""
    
    #  MOCK: 5 Volumes EBS (3 disponíveis/ociosos e 2 em uso)
    mock_ebs = {
        "Volumes": [
            {
                "VolumeId": "vol-0123456789abcdef0",
                "Size": 30,
                "State": "in-use",
                "VolumeType": "gp3",
                "CreateTime": datetime(2026, 5, 1, tzinfo=timezone.utc),
                "Attachments": [{"InstanceId": "i-abcdef01234567890", "State": "attached"}]
            },
            # Ocioso 1: 50GB gp2 (Criado há 15 dias)
            {
                "VolumeId": "vol-9876543210fedcba0",
                "Size": 50,
                "State": "available",
                "VolumeType": "gp2",
                "CreateTime": datetime.now(timezone.utc) - timedelta(days=15),
                "Attachments": []
            },
            # Ocioso 2: 200GB io2 (Disco caro ocioso! Criado há 5 dias)
            {
                "VolumeId": "vol-aaaaabbbbbccccc11",
                "Size": 200,
                "State": "available",
                "VolumeType": "io2",
                "CreateTime": datetime.now(timezone.utc) - timedelta(days=5),
                "Attachments": []
            },
            # Ocioso 3: 80GB gp3 (Criado há 30 dias)
            {
                "VolumeId": "vol-dddddeeeeefffff22",
                "Size": 80,
                "State": "available",
                "VolumeType": "gp3",
                "CreateTime": datetime.now(timezone.utc) - timedelta(days=30),
                "Attachments": []
            },
            {
                "VolumeId": "vol-777778888899999aa",
                "Size": 100,
                "State": "in-use",
                "VolumeType": "gp3",
                "CreateTime": datetime(2026, 2, 10, tzinfo=timezone.utc),
                "Attachments": [{"InstanceId": "i-9876543210abcdef1", "State": "attached"}]
            }
        ]
    }
    
    #  MOCK: 4 Elastic IPs (2 associados, 2 abandonados gerando cobrança)
    mock_eip = {
        "Addresses": [
            {
                "PublicIp": "54.210.43.12",
                "AllocationId": "eipalloc-0123456789abcdef0",
                "InstanceId": "i-abcdef01234567890",
                "AssociationId": "eipassoc-01234567"
            },
            # Abandonado 1
            {
                "PublicIp": "34.200.15.99",
                "AllocationId": "eipalloc-9876543210fedcba0",
                "Domain": "vpc"
            },
            # Abandonado 2
            {
                "PublicIp": "18.232.45.112",
                "AllocationId": "eipalloc-bbbbbbcccccc11111",
                "Domain": "vpc"
            },
            {
                "PublicIp": "52.8.124.9",
                "AllocationId": "eipalloc-222223333344444",
                "InstanceId": "i-9876543210abcdef1",
                "AssociationId": "eipassoc-88888888"
            }
        ]
    }

    # MOCK: Frota de Instâncias EC2 (Múltiplos cenários de Right-Sizing)
    mock_ec2 = {
        "Reservations": [
            {
                "Instances": [
                    # Ociosa 1: t3.medium com 4.2% CPU
                    {
                        "InstanceId": "i-1234567890abcdef0",
                        "InstanceType": "t3.medium",
                        "State": {"Name": "running"},
                        "LaunchTime": datetime(2026, 6, 1, tzinfo=timezone.utc),
                        "CpuUtilizationAverage": 4.2 
                    },
                    # Saudável: t3.large com 78.5% CPU (Deve ser ignorada pelo auditor)
                    {
                        "InstanceId": "i-9876543210abcdef1",
                        "InstanceType": "t3.large",
                        "State": {"Name": "running"},
                        "LaunchTime": datetime(2026, 6, 15, tzinfo=timezone.utc),
                        "CpuUtilizationAverage": 78.5
                    },
                    # Ociosa 2: m5.xlarge (Instância caríssima com 1.8% CPU!)
                    {
                        "InstanceId": "i-aaaa1111bbbb2222c",
                        "InstanceType": "m5.xlarge",
                        "State": {"Name": "running"},
                        "LaunchTime": datetime(2026, 5, 20, tzinfo=timezone.utc),
                        "CpuUtilizationAverage": 1.8
                    },
                    # Ociosa 3: t3.micro com 8.9% CPU
                    {
                        "InstanceId": "i-cccc3333dddd4444e",
                        "InstanceType": "t3.micro",
                        "State": {"Name": "running"},
                        "LaunchTime": datetime(2026, 6, 20, tzinfo=timezone.utc),
                        "CpuUtilizationAverage": 8.9
                    },
                    # Desligada: (Deve ser ignorada porque não está gastando CPU ativa)
                    {
                        "InstanceId": "i-eeee5555ffff6666g",
                        "InstanceType": "t3.scratch",
                        "State": {"Name": "stopped"},
                        "LaunchTime": datetime(2026, 1, 1, tzinfo=timezone.utc),
                        "CpuUtilizationAverage": 0.0
                    }
                ]
            }
        ]
    }
    
    return mock_ebs, mock_eip, mock_ec2