package database

import (
	"log"
	"math"
	"math/rand"
	"time"
	"healthcare-backend/pkg/models"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var DB *gorm.DB

func InitDB() {
	var err error
	DB, err = gorm.Open(sqlite.Open("clinical.db"), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database")
	}
	DB.AutoMigrate(&models.PatientData{}, &models.Feedback{})
	log.Println("✅ Database Migrated (SQLite)")
	seedDemoData()
}

func seedDemoData() {
	var count int64
	DB.Model(&models.PatientData{}).Count(&count)
	if count == 0 {
		log.Println("🌱 Seeding random patient data...")
		rand.Seed(time.Now().UnixNano())

		// Generate 10 random patients
		for i := 0; i < 10; i++ {
			age := 25 + rand.Intn(60)
			gender := []string{"Male", "Female"}[rand.Intn(2)]
			
			// Correlate metrics with "risk profiles"
			riskProfile := rand.Intn(3) // 0: Healthy, 1: Moderate, 2: High Risk
			
			systolic := 110 + rand.Intn(20)
			diastolic := 70 + rand.Intn(15)
			bmi := 22.0 + rand.Float64()*5.0
			cholesterol := 160 + rand.Intn(40)
			glucose := 80 + rand.Intn(20)
			smoking := "No"
			
			if riskProfile == 1 { // Moderate
				systolic += 20
				diastolic += 10
				bmi += 5.0
				cholesterol += 40
				glucose += 30
				if rand.Float32() > 0.7 { smoking = "Yes" }
			} else if riskProfile == 2 { // High Risk
				systolic += 40
				diastolic += 20
				bmi += 10.0
				cholesterol += 80
				glucose += 60
				if rand.Float32() > 0.4 { smoking = "Yes" }
			}

			patient := models.PatientData{
				Age: age, 
				Gender: gender, 
				SystolicBP: systolic, 
				DiastolicBP: diastolic, 
				Glucose: glucose, 
				BMI: math.Round(bmi*10)/10, 
				Cholesterol: cholesterol, 
				HeartRate: 60 + rand.Intn(40), 
				Steps: 1000 + rand.Intn(9000), 
				Smoking: smoking,
			}
			DB.Create(&patient)
		}
		
		log.Println("🚀 Seeded 10 Random Demo Patients")
	}
}
