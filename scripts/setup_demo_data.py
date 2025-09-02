"""
Scenario-Based Demo Data Setup for Z-Cred

Creates realistic demo users representing key market segments:
1. Rural Entrepreneur (SHG Member)
2. Urban Gig Worker (Delivery Partner) 
3. Small Business Owner (Tailoring Business)

Each scenario showcases different aspects of alternative credit scoring.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from local_db import Database
import json
from datetime import datetime, timedelta


def setup_demo_data():
    """Setup scenario-based demo users with compelling stories"""
    db = Database()

    # Scenario 1: Rural Entrepreneur - Meera Devi
    meera_data = {
        "id": "scenario_meera",
        "name": "Meera Devi",
        "phone": "+91-9876501001",
        "email": "meera@selfhelp.in",
        "age": 32,
        "gender": "Female",
        "location": "Jaipur District, Rajasthan",
        "occupation": "Handicraft Artisan & SHG Leader",
        "monthly_income": 18000,
        "income": 18000,
        "employment_length": 4,
        "debt_to_income": 0.12,
        "credit_utilization": 0.00,  # No formal credit
        "payment_history_score": 85,
        "account_diversity": 1,
        "savings_rate": 0.22,
        "education_level": "10th Standard",
        
        # Trust Score Components
        "behavioral_score": 0.75,  # Strong payment discipline
        "social_score": 0.88,      # Excellent community standing
        "digital_score": 0.65,     # Limited but consistent
        "overall_trust_score": 0.77,
        
        # Scenario-specific data
        "alternative_data": json.dumps({
            "payment_history": {
                "electricity_bills": {
                    "avg_monthly": 450,
                    "payment_regularity": 0.85,
                    "on_time_payments": 17,
                    "late_payments": 3
                },
                "mobile_recharge": {
                    "frequency": "monthly",
                    "amount_consistency": 0.92,
                    "avg_amount": 299
                }
            },
            "social_proof": {
                "shg_membership": {
                    "role": "group_leader",
                    "tenure": "4_years",
                    "group_size": 12,
                    "repayment_rate": 0.98,
                    "leadership_rating": 4.6
                },
                "community_endorsements": {
                    "local_testimonials": 8,
                    "business_references": 5,
                    "community_rating": 4.4
                }
            },
            "digital_footprint": {
                "device_stability": {
                    "primary_device": "feature_phone_3_years",
                    "number_porting": 0
                },
                "transaction_sms": {
                    "banking_activity": "regular_savings",
                    "govt_transfer_receipt": "consistent"
                }
            }
        }),
        "story": "SHG leader seeking business expansion capital",
        "scenario_type": "rural_entrepreneur",
        "credit_need": "₹25,000 for handicraft equipment",
        "demo_stage": "trust_building",
        "created_at": datetime.now().isoformat(),
    }

    # Scenario 2: Urban Gig Worker - Arjun Krishnan
    arjun_data = {
        "id": "scenario_arjun",
        "name": "Arjun Krishnan",
        "phone": "+91-9876502002",
        "email": "arjun@delivery.in",
        "age": 26,
        "gender": "Male",
        "location": "Bangalore, Karnataka",
        "occupation": "Food Delivery Partner",
        "monthly_income": 32000,
        "income": 32000,
        "employment_length": 2,
        "debt_to_income": 0.08,
        "credit_utilization": 0.35,  # Has credit card
        "payment_history_score": 88,
        "account_diversity": 3,
        "savings_rate": 0.25,
        "education_level": "Engineering Graduate",
        
        # Trust Score Components
        "behavioral_score": 0.82,  # Excellent payment discipline
        "social_score": 0.76,      # Good professional network
        "digital_score": 0.89,     # High digital proficiency
        "overall_trust_score": 0.83,
        
        # Scenario-specific data
        "alternative_data": json.dumps({
            "platform_earnings": {
                "swiggy_consistency": 0.88,
                "zomato_consistency": 0.82,
                "uber_consistency": 0.75,
                "weekly_earnings_trend": "stable_growth",
                "peak_hour_efficiency": 0.92
            },
            "digital_footprint": {
                "platform_ratings": {
                    "swiggy_rating": 4.7,
                    "zomato_rating": 4.6,
                    "completion_rate": 0.97
                },
                "device_usage": {
                    "smartphone": "flagship_2_years",
                    "gps_accuracy": 0.98,
                    "app_usage_pattern": "professional_focused"
                },
                "transaction_velocity": {
                    "daily_transactions": 25,
                    "digital_wallet_score": 0.94,
                    "cashless_preference": 0.85
                }
            },
            "social_proof": {
                "gig_community": {
                    "delivery_partner_groups": 3,
                    "peer_recommendations": 12,
                    "community_rating": 4.5
                },
                "professional_references": {
                    "linkedin_endorsements": 25,
                    "skill_certifications": 4
                }
            }
        }),
        "story": "Gig worker seeking electric vehicle financing",
        "scenario_type": "urban_gig_worker", 
        "credit_need": "₹80,000 for electric bike purchase",
        "demo_stage": "digital_champion",
        "created_at": datetime.now().isoformat(),
    }

    # Scenario 3: Small Business Owner - Fatima Beevi
    fatima_data = {
        "id": "scenario_fatima",
        "name": "Fatima Beevi",
        "phone": "+91-9876503003",
        "email": "fatima@tailoring.in",
        "age": 38,
        "gender": "Female",
        "location": "Kochi, Kerala",
        "occupation": "Tailoring Business Owner",
        "monthly_income": 45000,
        "income": 45000,
        "employment_length": 12,
        "debt_to_income": 0.15,
        "credit_utilization": 0.45,
        "payment_history_score": 94,
        "account_diversity": 5,
        "savings_rate": 0.28,
        "education_level": "12th + Diploma",
        
        # Trust Score Components
        "behavioral_score": 0.87,  # Excellent business management
        "social_score": 0.91,      # Outstanding business reputation
        "digital_score": 0.72,     # Growing digital adoption
        "overall_trust_score": 0.85,
        
        # Scenario-specific data
        "alternative_data": json.dumps({
            "business_payments": {
                "electricity_commercial": {
                    "avg_monthly": 2800,
                    "payment_regularity": 0.94,
                    "growth_trend": "stable_increase"
                },
                "rent_payment": {
                    "amount": 8000,
                    "tenure": "36_months",
                    "on_time_rate": 1.0
                },
                "supplier_payments": {
                    "fabric_suppliers": 3,
                    "early_payment_discount": "utilized",
                    "relationship_score": 4.6
                }
            },
            "social_proof": {
                "customer_base": {
                    "regular_customers": 85,
                    "customer_retention": 0.89,
                    "google_rating": 4.5,
                    "referral_rate": 0.65
                },
                "business_network": {
                    "supplier_relationships": 8,
                    "trade_association_member": True,
                    "community_standing": "respected"
                },
                "professional_growth": {
                    "skill_certifications": 3,
                    "design_competitions": "state_level_winner"
                }
            },
            "digital_footprint": {
                "online_presence": {
                    "whatsapp_business": "active_customer_communication",
                    "facebook_page": "weekly_posts",
                    "google_my_business": "verified_claimed"
                },
                "digital_payments": {
                    "upi_adoption": "recent_6_months",
                    "digital_transaction_rate": 0.35
                }
            },
            "business_performance": {
                "revenue_patterns": {
                    "monthly_avg": 45000,
                    "growth_rate": "15%_annual",
                    "profit_margin": "35%"
                },
                "operational_metrics": {
                    "orders_completed": 156,
                    "delivery_punctuality": 0.92,
                    "quality_rating": 4.6,
                    "repeat_order_rate": 0.78
                }
            }
        }),
        "story": "Established business owner seeking expansion capital",
        "scenario_type": "small_business_owner",
        "credit_need": "₹1,50,000 for business expansion",
        "demo_stage": "business_builder",
        "created_at": datetime.now().isoformat(),
    }

    # Store demo users
    demo_users = [meera_data, arjun_data, fatima_data]

    for user in demo_users:
        try:
            # Check if user already exists
            existing_user = None
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM applicants WHERE email = ?", (user['email'],))
                    result = cursor.fetchone()
                    if result:
                        existing_user = result[0]
            except Exception:
                pass
            
            if existing_user:
                print(f" ♻️  Demo user already exists: {user['name']} ({user['scenario_type']})")
                # Update existing user with latest scenario data
                try:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        # Parse alternative data JSON
                        alt_data = json.loads(user['alternative_data'])
                        
                        cursor.execute("""
                            UPDATE applicants SET 
                                name = ?, phone = ?, email = ?, age = ?, gender = ?, location = ?,
                                occupation = ?, monthly_income = ?, overall_trust_score = ?,
                                utility_payment_history = ?, mfi_loan_history = ?, 
                                social_proof_data = ?, digital_footprint = ?
                            WHERE email = ?
                        """, (
                            user['name'], user['phone'], user['email'], user['age'], user['gender'], user['location'],
                            user['occupation'], user['monthly_income'], user['overall_trust_score'],
                            json.dumps(alt_data.get('payment_history', {})),
                            json.dumps(alt_data.get('payment_history', {})),
                            json.dumps(alt_data.get('social_proof', {})),
                            json.dumps(alt_data.get('digital_footprint', {})),
                            user['email']
                        ))
                        conn.commit()
                        
                    # Update trust scores
                    db.update_trust_score(
                        existing_user,
                        user['behavioral_score'],
                        user['social_score'], 
                        user['digital_score']
                    )
                    print(f" ✅ Updated existing demo user: {user['name']}")
                except Exception as e:
                    print(f" ⚠️  Could not update existing user {user['name']}: {e}")
            else:
                # Create new user
                applicant_id = db.create_applicant(user)
                if applicant_id:
                    print(f" ✅ Created scenario user: {user['name']} ({user['scenario_type']})")
                    
                    # Update with alternative data fields
                    try:
                        with db.get_connection() as conn:
                            cursor = conn.cursor()
                            alt_data = json.loads(user['alternative_data'])
                            
                            cursor.execute("""
                                UPDATE applicants SET 
                                    overall_trust_score = ?, utility_payment_history = ?, 
                                    mfi_loan_history = ?, social_proof_data = ?, digital_footprint = ?
                                WHERE id = ?
                            """, (
                                user['overall_trust_score'],
                                json.dumps(alt_data.get('payment_history', {})),
                                json.dumps(alt_data.get('payment_history', {})),
                                json.dumps(alt_data.get('social_proof', {})),
                                json.dumps(alt_data.get('digital_footprint', {})),
                                applicant_id
                            ))
                            conn.commit()
                    except Exception as e:
                        print(f" ⚠️  Could not update alternative data for {user['name']}: {e}")
                    
                    # Add trust score progression
                    db.update_trust_score(
                        applicant_id,
                        user['behavioral_score'],
                        user['social_score'], 
                        user['digital_score']
                    )
                    
                    # Log consent for demo
                    db.log_consent(
                        applicant_id,
                        'demo_scenario',
                        'comprehensive_assessment',
                        True,
                        {'demo_type': user['scenario_type'], 'setup_date': datetime.now().isoformat()}
                    )
                else:
                    print(f" ⚠️  Could not create user {user['name']}")
                    
        except Exception as e:
            print(f" ❌ Error processing {user['name']}: {e}")

    print(f"\n 🎯 Scenario demo data setup complete! {len(demo_users)} users ready.")
    print(f" 📊 Scenarios: Rural Entrepreneur, Urban Gig Worker, Small Business Owner")
    return demo_users


def get_scenario_credentials():
    """Get scenario-based login credentials"""
    return {
        "meera": {
            "email": "meera@selfhelp.in",
            "password": "demo123",
            "scenario": "Rural Entrepreneur - SHG Leader",
            "trust_score": "77/100",
            "credit_need": "₹25,000 for handicraft equipment",
            "key_strengths": ["Community leadership", "Payment consistency", "Social proof"]
        },
        "arjun": {
            "email": "arjun@delivery.in", 
            "password": "demo123",
            "scenario": "Urban Gig Worker - Delivery Partner",
            "trust_score": "83/100",
            "credit_need": "₹80,000 for electric vehicle",
            "key_strengths": ["High platform ratings", "Digital proficiency", "Income diversification"]
        },
        "fatima": {
            "email": "fatima@tailoring.in",
            "password": "demo123", 
            "scenario": "Small Business Owner - Tailoring Business",
            "trust_score": "85/100", 
            "credit_need": "₹1,50,000 for business expansion",
            "key_strengths": ["12-year business track record", "Excellent customer retention", "Growth trajectory"]
        }
    }


def cleanup_all_existing_data():
    """Remove ALL existing data except new demo scenarios"""
    db = Database()
    
    def _cleanup_all_data():
        """Internal cleanup function to remove all existing data"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Keep only our new demo scenario users
            demo_scenario_emails = [
                "meera@selfhelp.in",
                "arjun@delivery.in", 
                "fatima@tailoring.in"
            ]
            
            # Build placeholders for SQL IN clause
            placeholders = ",".join("?" * len(demo_scenario_emails))
            
            try:
                # Remove all applicants EXCEPT our demo scenarios
                cursor.execute(
                    f"DELETE FROM applicants WHERE email NOT IN ({placeholders})",
                    demo_scenario_emails
                )
                removed_count = cursor.rowcount
                print(f" 🗑️  Removed {removed_count} non-demo users from applicants table")
                
                # Clean up related tables - trust_scores (keep only demo scenarios)
                cursor.execute("""
                    DELETE FROM trust_scores 
                    WHERE applicant_id NOT IN (
                        SELECT id FROM applicants WHERE email IN ({})
                    )
                """.format(placeholders), demo_scenario_emails)
                removed_trust_scores = cursor.rowcount
                print(f" 🗑️  Removed {removed_trust_scores} non-demo trust score records")
                
                # Clean up consent_logs (keep only demo scenarios)
                cursor.execute("""
                    DELETE FROM consent_logs 
                    WHERE applicant_id NOT IN (
                        SELECT id FROM applicants WHERE email IN ({})
                    )
                """.format(placeholders), demo_scenario_emails)
                removed_consent_logs = cursor.rowcount
                print(f" 🗑️  Removed {removed_consent_logs} non-demo consent log records")
                
                # Clean up any other related data tables if they exist
                try:
                    # Check if there are other tables with applicant references
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    for table in tables:
                        if table.startswith('sqlite_') or table in ['applicants', 'trust_scores', 'consent_logs']:
                            continue  # Skip system tables and already cleaned tables
                        
                        # Try to clean tables that might have applicant_id references
                        try:
                            cursor.execute(f"PRAGMA table_info({table})")
                            columns = [col[1] for col in cursor.fetchall()]
                            
                            if 'applicant_id' in columns:
                                cursor.execute(f"""
                                    DELETE FROM {table} 
                                    WHERE applicant_id NOT IN (
                                        SELECT id FROM applicants WHERE email IN ({placeholders})
                                    )
                                """, demo_scenario_emails)
                                removed_other = cursor.rowcount
                                if removed_other > 0:
                                    print(f" 🗑️  Removed {removed_other} non-demo records from {table}")
                        except Exception as e:
                            # Some tables might not have applicant_id, that's fine
                            pass
                            
                except Exception as e:
                    print(f" ⚠️  Could not clean additional tables: {e}")
                
                conn.commit()
                print(f" ✅ Database cleanup completed - only demo scenario data remains")
                
            except Exception as e:
                print(f" ❌ Error during cleanup: {e}")
                conn.rollback()
    
    try:
        db.execute_with_retry(_cleanup_all_data)
        print(" ✅ All existing data cleanup completed")
    except Exception as e:
        print(f" ⚠️  Error during cleanup: {e}")


def cleanup_old_demo_data():
    """Remove old demo data before setting up new scenarios - DEPRECATED"""
    # This function is now replaced by cleanup_all_existing_data()
    print(" ℹ️  Using comprehensive cleanup instead of old demo cleanup")
    cleanup_all_existing_data()


if __name__ == "__main__":
    print(" 🚀 Setting up Z-Cred Scenario-Based Demo Data...")
    print(" 🧹 This will remove ALL existing data except demo scenarios")
    
    # Clean up ALL existing data first (not just old demo data)
    cleanup_all_existing_data()
    
    # Setup new scenario data
    users = setup_demo_data()

    print("\n 🔐 Demo Credentials:")
    print(" " + "="*60)
    creds = get_scenario_credentials()
    for name, info in creds.items():
        print(f" 👤 {name.title()}: {info['email']} / {info['password']}")
        print(f"    📋 {info['scenario']}")
        print(f"    ⭐ Trust Score: {info['trust_score']}")
        print(f"    💰 Credit Need: {info['credit_need']}")
        print(f"    💪 Strengths: {', '.join(info['key_strengths'])}")
        print(" " + "-"*60)
    
    print("\n 📚 Documentation:")
    print(" 📖 Detailed scenarios: docs/DEMO_SCENARIOS.md")
    print(" 📝 Individual scenarios: docs/SCENARIO_*.md")
    print("\n ✨ Ready for hackathon demonstration!")
    print("\n 🎯 Database now contains ONLY demo scenario data!")

    print("\n Ready for hackathon demo!")
