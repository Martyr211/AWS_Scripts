$path = "../AWS Keypair/DevOps.pem"
icacls.exe $path /reset
icacls.exe $path /GRANT:R 
icacls.exe $path /inheritance:r
