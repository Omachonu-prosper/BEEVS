#!/usr/bin/env python3
"""
Script to create a super admin user for the BEEVS application.
This script prompts for admin details and creates a super admin account.
"""

import sys
import os
from getpass import getpass

# Add the parent directory to the path to import the beevs module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from beevs import create_app, db
from beevs.models import Admin, AdminRole
from beevs.utils import validate_email, validate_password_strength


def create_super_admin():
    """Create a super admin user"""
    print("=== BEEVS Super Admin Creation Script ===\n")
    
    # Get admin details
    name = input("Enter super admin full name: ").strip()
    if not name:
        print("Error: Name cannot be empty")
        return False
    
    email = input("Enter super admin email: ").strip().lower()
    if not email:
        print("Error: Email cannot be empty")
        return False
    
    if not validate_email(email):
        print("Error: Invalid email format")
        return False
    
    # Get password with confirmation
    while True:
        password = getpass("Enter super admin password: ")
        if not password:
            print("Error: Password cannot be empty")
            continue
            
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            print(f"Error: {message}")
            continue
            
        confirm_password = getpass("Confirm password: ")
        if password != confirm_password:
            print("Error: Passwords do not match")
            continue
        break
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        try:
            # Check if admin with this email already exists
            existing_admin = Admin.query.filter_by(email=email).first()
            if existing_admin:
                print(f"Error: An admin with email '{email}' already exists")
                return False
            
            # Create new super admin
            super_admin = Admin(
                name=name,
                email=email,
                role=AdminRole.SUPER_ADMIN
            )
            
            # Set password (this will hash it automatically)
            super_admin.password = password
            
            # Add to database
            db.session.add(super_admin)
            db.session.commit()
            
            print(f"\n✅ Super admin created successfully!")
            print(f"Name: {super_admin.name}")
            print(f"Email: {super_admin.email}")
            print(f"Role: {super_admin.role.value}")
            print(f"Created at: {super_admin.created_at}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating super admin: {str(e)}")
            return False


def main():
    """Main function"""
    try:
        success = create_super_admin()
        if success:
            print("\nSuper admin account is ready to use!")
            sys.exit(0)
        else:
            print("\nFailed to create super admin account.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()