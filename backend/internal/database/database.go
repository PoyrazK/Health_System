package database

import (
	"log"
	"healthcare-backend/internal/models"

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
		// 1. Ahmet Amca - The Emergency Case
		ahmet := models.PatientData{Age: 67, Gender: "Male", SystolicBP: 185, DiastolicBP: 110, Glucose: 240, BMI: 32.5, Cholesterol: 245, HeartRate: 98, Steps: 1200, Smoking: "Yes"}
		DB.Create(&ahmet)
		
		// 2. Zeynep Hanim - The Stable Case
		zeynep := models.PatientData{Age: 42, Gender: "Female", SystolicBP: 118, DiastolicBP: 78, Glucose: 95, BMI: 22.1, Cholesterol: 180, HeartRate: 72, Steps: 8500, Smoking: "No"}
		DB.Create(&zeynep)
		
		log.Println("🚀 Demo Patients Seeded: Ahmet Amca & Zeynep Hanim")
	}
}
