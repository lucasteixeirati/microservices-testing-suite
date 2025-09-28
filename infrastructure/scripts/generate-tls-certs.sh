#!/bin/bash
# Generate TLS certificates for microservices

# Create CA private key
openssl genrsa -out ca.key 4096

# Create CA certificate
openssl req -new -x509 -key ca.key -sha256 -subj "/C=US/ST=CA/O=Microservices/CN=microservices-ca" -days 3650 -out ca.crt

# Create server private key
openssl genrsa -out server.key 4096

# Create certificate signing request
openssl req -new -key server.key -out server.csr -config <(
cat <<EOF
[req]
default_bits = 4096
prompt = no
distinguished_name = req_distinguished_name
req_extensions = req_ext

[req_distinguished_name]
C=US
ST=CA
O=Microservices
CN=microservices.local

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = microservices.local
DNS.2 = *.microservices.local
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF
)

# Generate server certificate
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -extensions req_ext -extfile <(
cat <<EOF
[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = microservices.local
DNS.2 = *.microservices.local
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF
)

# Update Kubernetes secret with base64 encoded certificates
TLS_CRT=$(base64 -w 0 server.crt)
TLS_KEY=$(base64 -w 0 server.key)

# Update the secret file
sed -i "s|LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t|$TLS_CRT|g" ../istio/tls-secret.yaml
sed -i "s|LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t|$TLS_KEY|g" ../istio/tls-secret.yaml

echo "TLS certificates generated and updated in tls-secret.yaml"