#!/usr/bin/env python3
"""
Enterprise Folder System Test Script
Tests all folder operations comprehensively
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_folder_system():
    """Test complete folder system"""
    async with aiohttp.ClientSession() as session:
        print("🧪 ENTERPRISE FOLDER SYSTEM TEST")
        print("=" * 50)
        
        # Test 1: Get categories
        print("\n📋 Test 1: Get Categories")
        async with session.get(f"{BASE_URL}/categories/") as resp:
            if resp.status == 200:
                categories = await resp.json()
                print(f"✅ Found {len(categories)} categories:")
                for cat in categories:
                    print(f"   - {cat['name']} (slug: {cat['slug']})")
            else:
                print(f"❌ Failed: {resp.status}")
                return
        
        # Use first category
        if categories:
            test_category = categories[0]['slug']
            print(f"\n🎯 Using category: {test_category}")
        else:
            print("❌ No categories found!")
            return
        
        # Test 2: Get folders for category
        print(f"\n📁 Test 2: Get Folders for '{test_category}'")
        async with session.get(f"{BASE_URL}/folders/categories/{test_category}/folders") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Category: {data['category']['name']}")
                print(f"   Total folders: {data['total_folders']}")
                print(f"   Active folders: {data['total_active']}")
                if data['folders']:
                    for folder in data['folders']:
                        print(f"   - {folder['name']} (ID: {folder['id']})")
            else:
                error = await resp.text()
                print(f"❌ Failed: {resp.status} - {error}")
        
        # Test 3: Create main folder
        print(f"\n➕ Test 3: Create Main Folder")
        form_data = aiohttp.FormData()
        form_data.add_field('name', f'Test Hauptordner {datetime.now().strftime("%H%M%S")}')
        form_data.add_field('description', 'Enterprise Test Folder')
        form_data.add_field('color', '#0066CC')
        form_data.add_field('icon', '📁')
        
        async with session.post(
            f"{BASE_URL}/folders/categories/{test_category}/folders",
            data=form_data
        ) as resp:
            if resp.status == 200:
                main_folder = await resp.json()
                print(f"✅ Created folder: {main_folder['name']}")
                print(f"   ID: {main_folder['id']}")
                print(f"   Slug: {main_folder['slug']}")
                main_folder_id = main_folder['id']
            else:
                error = await resp.text()
                print(f"❌ Failed: {resp.status} - {error}")
                return
        
        # Test 4: Create subfolder
        print(f"\n➕ Test 4: Create Subfolder")
        form_data = aiohttp.FormData()
        form_data.add_field('name', f'Test Unterordner {datetime.now().strftime("%H%M%S")}')
        form_data.add_field('description', 'Enterprise Sub Folder')
        form_data.add_field('parent_id', main_folder_id)
        form_data.add_field('color', '#00AA44')
        
        async with session.post(
            f"{BASE_URL}/folders/categories/{test_category}/folders",
            data=form_data
        ) as resp:
            if resp.status == 200:
                sub_folder = await resp.json()
                print(f"✅ Created subfolder: {sub_folder['name']}")
                print(f"   Parent: {sub_folder['parent_folder_id']}")
                sub_folder_id = sub_folder['id']
            else:
                error = await resp.text()
                print(f"❌ Failed: {resp.status} - {error}")
        
        # Test 5: Get updated folder tree
        print(f"\n🌳 Test 5: Get Updated Folder Tree")
        async with session.get(f"{BASE_URL}/folders/categories/{test_category}/folders") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Found {data['total_folders']} folders")
                
                def print_tree(folders, indent=0):
                    for folder in folders:
                        print("   " + "  " * indent + f"└─ {folder['name']} ({folder['file_count']} files)")
                        if folder['children']:
                            print_tree(folder['children'], indent + 1)
                
                print_tree(data['folders'])
            else:
                error = await resp.text()
                print(f"❌ Failed: {resp.status} - {error}")
        
        # Test 6: Update folder
        print(f"\n✏️ Test 6: Update Folder")
        form_data = aiohttp.FormData()
        form_data.add_field('name', 'Updated Test Folder')
        form_data.add_field('color', '#FF0000')
        
        async with session.put(
            f"{BASE_URL}/folders/folders/{main_folder_id}",
            data=form_data
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Updated folder successfully")
                print(f"   Updated fields: {result['updated_fields']}")
            else:
                error = await resp.text()
                print(f"❌ Failed: {resp.status} - {error}")
        
        # Test 7: Delete folder (without force)
        print(f"\n🗑️ Test 7: Delete Folder (soft)")
        async with session.delete(f"{BASE_URL}/folders/folders/{sub_folder_id}") as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ {result['message']}")
                print(f"   Deleted: {result['folder_name']}")
            else:
                error = await resp.text()
                print(f"❌ Failed: {resp.status} - {error}")
        
        # Test 8: Delete folder with force
        print(f"\n🗑️ Test 8: Delete Folder (force)")
        async with session.delete(f"{BASE_URL}/folders/folders/{main_folder_id}?force=true") as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ {result['message']}")
                print(f"   Deleted subfolders: {result['deleted_subfolders']}")
                print(f"   Deleted files: {result['deleted_files']}")
            else:
                error = await resp.text()
                print(f"❌ Failed: {resp.status} - {error}")
        
        print("\n" + "=" * 50)
        print("✅ FOLDER SYSTEM TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_folder_system())