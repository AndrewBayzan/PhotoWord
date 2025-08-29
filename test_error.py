#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app

def test_register():
    """Тестирует регистрацию и показывает точную ошибку"""
    app = create_app()
    
    with app.test_client() as client:
        print("Тестирование регистрации...")
        response = client.post('/register', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        print(f"Статус ответа: {response.status_code}")
        print(f"Содержимое ответа: {response.data.decode('utf-8')}")

if __name__ == "__main__":
    test_register()
