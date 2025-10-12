"""
Wait for 5 samples to be generated, then check CSV quality
"""
import time
import pandas as pd
from pathlib import Path

csv_path = Path("data/training_data.csv")

print("⏳ Waiting for 5 samples to be generated...")
print("   (Each sample takes 1-3 minutes)")

last_count = 0
while True:
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            count = len(df)
            
            if count != last_count:
                print(f"\n✅ {count} sample(s) generated")
                last_count = count
            
            if count >= 5:
                print("\n" + "="*70)
                print("🎉 5 SAMPLES COMPLETE! Checking CSV quality...")
                print("="*70)
                
                # Check variance in key columns
                print("\n📊 Feature Variance Check:")
                print(f"   num_nodes: {df['num_nodes'].nunique()} unique values → {sorted(df['num_nodes'].unique())}")
                print(f"   num_edges: {df['num_edges'].nunique()} unique values → {sorted(df['num_edges'].unique())}")
                print(f"   max_loops: {df['max_loops'].nunique()} unique values → {sorted(df['max_loops'].unique())}")
                print(f"   avg_personal_score: {df['avg_personal_score'].nunique()} unique values")
                print(f"   clustering_coefficient: {df['clustering_coefficient'].nunique()} unique values")
                
                # Check if NOT all zeros
                print("\n🔍 Zero Check:")
                zero_cols = []
                for col in df.columns:
                    if df[col].dtype in ['float64', 'int64']:
                        if (df[col] == 0).all():
                            zero_cols.append(col)
                
                if zero_cols:
                    print(f"   ❌ All zeros: {zero_cols}")
                else:
                    print(f"   ✅ No columns with all zeros")
                
                # Check constant columns
                print("\n📈 Constant Column Check:")
                constant_cols = []
                for col in df.columns:
                    if df[col].dtype in ['float64', 'int64']:
                        if df[col].nunique() == 1:
                            constant_cols.append(col)
                
                if constant_cols:
                    print(f"   ⚠️  Constant: {constant_cols}")
                else:
                    print(f"   ✅ All columns have variance")
                
                # Show first 5 rows
                print("\n📋 First 5 rows:")
                print(df.head())
                
                # Final verdict
                print("\n" + "="*70)
                if len(zero_cols) == 0 and len(constant_cols) <= 2:
                    print("✅ CSV LOOKS GOOD! Variance detected.")
                    print("   You can proceed to generate more samples.")
                    print("\n💡 To generate 50 samples:")
                    print("   python main.py generate")
                    print("   Then enter: 20, 20, 10")
                else:
                    print("⚠️  CSV has issues. Need to check code.")
                print("="*70)
                break
        except Exception as e:
            pass  # CSV being written
    
    time.sleep(10)  # Check every 10 seconds
