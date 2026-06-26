#!/bin/bash

echo "Скачивание тестовых PDF-файлов..."

curl -L -o test1.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test2.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test3.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test4.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test5.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test6.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test7.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test8.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test9.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -L -o test10.pdf "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

echo "Загрузка документов в систему..."

curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test1.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test2.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test3.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test4.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test5.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test6.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test7.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test8.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test9.pdf"
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test10.pdf"

echo "Готово!"