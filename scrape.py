from bs4 import BeautifulSoup
from flask import Flask, render_template, request

url = 'https://mono-tech.net/'
res = request.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
soup