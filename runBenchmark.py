from client import create_document_flow_client, WALLET_FILE_PATH

with open(WALLET_FILE_PATH, "r+") as open_wallet_file:
    client = create_document_flow_client(open_wallet_file, "localhost", 5001)

    client.run_benchmarking(1)
