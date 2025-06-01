sudo aws ecr get-login-password --region us-east-1 |sudo  docker login --username AWS --password-stdin 841256950471.dkr.ecr.us-east-1.amazonaws.com
sudo docker build --platform=linux/amd64  -t finofai-scraper .
sudo docker tag finofai-scraper:latest 841256950471.dkr.ecr.us-east-1.amazonaws.com/finofai-scraper:latest
sudo docker push 841256950471.dkr.ecr.us-east-1.amazonaws.com/finofai-scraper:latest