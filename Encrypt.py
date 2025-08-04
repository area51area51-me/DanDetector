#Encode V1
#This is a program that will encrypt personal data to be transferred as plain text
#It will encrypt the data, save it to file and decrypt again to verify data integrity.
#Version changelog
#8-3-25 V1
#Implementation

from cryptography.fernet import Fernet

#retrieve key
f=open('key.txt','rb')
key=f.read()
f.close()
#print(key)

#Retrieve data
f = open('data.csv', 'r')
data=f.read()
f.close()

#encrypt
fernet = Fernet(key)
encData = fernet.encrypt(data.encode())
print('encoded')

#output encrypted data to transfer
f = open('data.txt','wb')
f.write(encData)
f.close()

#retrieve encrypted data
f=open('data.txt','rb')
encFile=f.read()
f.close()

#decrypt data
decData = fernet.decrypt(encFile).decode()
print('decoded')

#verify data integrity
if decData==data:
    print("success")
else:
    print("fail")

#output decrypted data for further use/verification
f=open('newData.csv','w')
f.write(decData)
f.close()
#print(decData)
