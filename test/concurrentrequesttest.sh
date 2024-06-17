# nginx限制最大请求为每秒20个,超过的会被立即拒绝

for i in {1..20}; do curl -X GET http://192.168.190.129/server/wxLogin; done

# 以下超过部分都被拒绝
#for i in {1..25}; do curl -X GET http://192.168.190.129/server/wxLogin; done
#for i in {1..50}; do curl -X GET http://192.168.190.129/server/wxLogin; done
#for i in {1..100}; do curl -X GET http://192.168.190.129/server/wxLogin; done

