#!/usr/bin/env python3
"""
Create Initial Admin User
Run this script once to create the first admin user for the system
"""

import asyncio
import os
import sys
from getpass import getpass
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database import DATABASE_URL
from auth.models import User, UserRole, Base
from auth.jwt_handler import JWTHandler
from datetime import datetime

def create_admin_user():
    """Create initial admin user"""
    
    print("🔐 StreamWorks Admin User Setup")
    print("=" * 40)
    
    # Get admin details
    username = input("Enter admin username: ").strip()
    if not username:
        print("❌ Username cannot be empty")
        sys.exit(1)
    
    email = input("Enter admin email: ").strip()
    if not email:
        print("❌ Email cannot be empty")
        sys.exit(1)
    
    password = getpass("Enter admin password: ").strip()
    if not password:
        print("❌ Password cannot be empty")
        sys.exit(1)
    
    password_confirm = getpass("Confirm admin password: ").strip()
    if password != password_confirm:
        print("❌ Passwords do not match")
        sys.exit(1)
    
    # Create database connection
    try:
        engine = create_engine(DATABASE_URL)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Create session
        with Session(engine) as db:
            
            # Check if admin already exists
            existing_admin = db.query(User).filter(
                User.username == username
            ).first()
            
            if existing_admin:
                print(f"❌ User '{username}' already exists")
                sys.exit(1)
            
            # Check if email already exists
            existing_email = db.query(User).filter(
                User.email == email
            ).first()
            
            if existing_email:
                print(f"❌ Email '{email}' already registered")
                sys.exit(1)
            
            # Create admin user
            hashed_password = JWTHandler.hash_password(password)
            
            admin_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                role=UserRole.ADMIN,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print(f"✅ Admin user '{username}' created successfully!")
            print(f"   User ID: {admin_user.id}")
            print(f"   Email: {admin_user.email}")
            print(f"   Role: {admin_user.role.value}")
            print(f"   Created: {admin_user.created_at}")
            print()
            print("🚀 You can now start the application and login with these credentials.")
            
    except Exception as e:
        print(f"❌ Failed to create admin user: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_admin_user()