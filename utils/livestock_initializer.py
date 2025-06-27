"""
Livestock System Initializer
Initialize species and product data into database
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database.database import Database
from database.models import Species, LivestockProduct

async def initialize_livestock_data():
    """Initialize all livestock species and products into database"""
    print("🚀 Initializing Livestock System Data...")
    
    db = Database(config.DATABASE_PATH)
    await db.init_db()
    
    try:
        # Initialize Fish Species
        print("🐟 Adding Fish Species...")
        for species_id, species_data in config.FISH_SPECIES.items():
            species = Species(
                species_id=species_id,
                name=species_data['name'],
                species_type='fish',
                tier=species_data['tier'],
                buy_price=species_data['buy_price'],
                sell_price=species_data['sell_price'],
                growth_time=species_data['growth_time'],
                special_ability=species_data['special_ability'],
                emoji=species_data['emoji']
            )
            await db.add_species(species)
            print(f"  ✅ Added: {species.name}")
        
        # Initialize Animal Species
        print("🐄 Adding Animal Species...")
        for species_id, species_data in config.ANIMAL_SPECIES.items():
            species = Species(
                species_id=species_id,
                name=species_data['name'],
                species_type='animal',
                tier=species_data['tier'],
                buy_price=species_data['buy_price'],
                sell_price=species_data['sell_price'],
                growth_time=species_data['growth_time'],
                special_ability=species_data['special_ability'],
                emoji=species_data['emoji']
            )
            await db.add_species(species)
            print(f"  ✅ Added: {species.name}")
        
        # Initialize Livestock Products
        print("🥛 Adding Livestock Products...")
        for species_id, product_data in config.LIVESTOCK_PRODUCTS.items():
            product = LivestockProduct(
                species_id=species_id,
                product_name=product_data['product_name'],
                product_emoji=product_data['product_emoji'],
                production_time=product_data['production_time'],
                sell_price=product_data['sell_price']
            )
            await db.add_livestock_product(product)
            print(f"  ✅ Added: {product.product_name} (from {species_id})")
        
        print("✅ Livestock System Data Initialized Successfully!")
        
        # Display summary
        fish_count = len(config.FISH_SPECIES)
        animal_count = len(config.ANIMAL_SPECIES)
        product_count = len(config.LIVESTOCK_PRODUCTS)
        
        print(f"""
📊 Livestock System Summary:
   🐟 Fish Species: {fish_count}
   🐄 Animal Species: {animal_count}
   🥛 Products: {product_count}
   💰 Total Investment Range: {get_price_range()}
        """)
        
    except Exception as e:
        print(f"❌ Error initializing livestock data: {e}")
        raise
    finally:
        await db.close()

def get_price_range():
    """Get price range summary"""
    all_species = {**config.FISH_SPECIES, **config.ANIMAL_SPECIES}
    
    min_price = min(species['buy_price'] for species in all_species.values())
    max_price = max(species['buy_price'] for species in all_species.values())
    
    return f"{min_price:,}🪙 - {max_price:,}🪙"

async def verify_livestock_data():
    """Verify that all data was inserted correctly"""
    print("🔍 Verifying Livestock Data...")
    
    db = Database(config.DATABASE_PATH)
    await db.init_db()
    
    try:
        # Check species
        fish_species = await db.get_all_species('fish')
        animal_species = await db.get_all_species('animal')
        
        print(f"✅ Fish Species in DB: {len(fish_species)}")
        print(f"✅ Animal Species in DB: {len(animal_species)}")
        
        # Check products
        product_count = 0
        for species_id in config.LIVESTOCK_PRODUCTS.keys():
            product = await db.get_livestock_product(species_id)
            if product:
                product_count += 1
        
        print(f"✅ Products in DB: {product_count}")
        
        # Display some examples
        print("\n🎯 Sample Species:")
        for species in fish_species[:3]:
            print(f"  {species.emoji} {species.name} - Tier {species.tier}")
        
        for species in animal_species[:3]:
            print(f"  {species.emoji} {species.name} - Tier {species.tier}")
            
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    # Run initialization
    asyncio.run(initialize_livestock_data())
    
    # Verify data
    asyncio.run(verify_livestock_data())
    
    print("🎉 Livestock System Ready!") 