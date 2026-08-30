// Synthetic MPLADS project dataset.
// Seeded with real MP / State / Constituency allocation data (MPLADS MP-wise allocation dataset).
// Risk scores, work stages, vendors, and flag reasons are synthetic and generated for demonstration only.

export const projects = [
  {
    "projectId": "MPLADS-00001",
    "workName": "Construction of Crematorium Shed, Sector 21",
    "description": "Construction of Crematorium Shed, Sector 21 under MPLADS scheme, recommended by D Ravikumar, MP for Viluppuram(Sc).",
    "category": "Others",
    "state": "Tamil Nadu",
    "constituency": "Viluppuram(Sc)",
    "mpName": "D Ravikumar",
    "authority": "District Panchayat Viluppuram(Sc)",
    "recommendationDate": "05 Apr 2022",
    "sanctionDate": "03 Aug 2024",
    "sanctionAmount": 14679000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 7230000,
    "lastExpenditureDate": "05 Feb 2024",
    "risk": {
      "overallScore": 37,
      "level": "LOW",
      "cost": {
        "score": 37,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 34,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 39,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 37,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00002",
    "workName": "Upgradation of Primary Health Centre, Gram 11",
    "description": "Upgradation of Primary Health Centre, Gram 11 under MPLADS scheme, recommended by D Ravikumar, MP for Viluppuram(Sc).",
    "category": "Health",
    "state": "Tamil Nadu",
    "constituency": "Viluppuram(Sc)",
    "mpName": "D Ravikumar",
    "authority": "District Panchayat Viluppuram(Sc)",
    "recommendationDate": "28 Feb 2023",
    "sanctionDate": "27 May 2024",
    "sanctionAmount": 18273000,
    "workStage": "Work in Progress",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 10505900,
    "lastExpenditureDate": "20 Sep 2026",
    "risk": {
      "overallScore": 41,
      "level": "MEDIUM",
      "cost": {
        "score": 20,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 43,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 41,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 78,
        "flagged": true,
        "reason": "A similar work description was found in Block 8, Tamil Nadu, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00003",
    "workName": "Construction of Drainage System, Gram 16",
    "description": "Construction of Drainage System, Gram 16 under MPLADS scheme, recommended by Amol Ramsing Kolhe, MP for Shirur.",
    "category": "Drainage",
    "state": "Maharashtra",
    "constituency": "Shirur",
    "mpName": "Amol Ramsing Kolhe",
    "authority": "Zila Parishad Shirur",
    "recommendationDate": "07 Jul 2023",
    "sanctionDate": "23 Dec 2024",
    "sanctionAmount": 31790000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 29609100,
    "lastExpenditureDate": "10 Dec 2024",
    "risk": {
      "overallScore": 66,
      "level": "MEDIUM",
      "cost": {
        "score": 33,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 72,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 86,
        "flagged": true,
        "reason": "Expenditure of ₹29,609,100 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 90,
        "flagged": true,
        "reason": "A similar work description was found in Panchayat 19, Maharashtra, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00004",
    "workName": "Construction of CC Road at Panchayat 3",
    "description": "Construction of CC Road at Panchayat 3 under MPLADS scheme, recommended by Manohar Lal, MP for Karnal.",
    "category": "Roads & Bridges",
    "state": "Haryana",
    "constituency": "Karnal",
    "mpName": "Manohar Lal",
    "authority": "Zila Parishad Karnal",
    "recommendationDate": "16 Oct 2023",
    "sanctionDate": "26 Aug 2022",
    "sanctionAmount": 28832000,
    "workStage": "Sanctioned",
    "vendorName": "M/s United Builders & Co.",
    "totalDisbursed": 1029300,
    "lastExpenditureDate": "04 Apr 2025",
    "risk": {
      "overallScore": 52,
      "level": "MEDIUM",
      "cost": {
        "score": 85,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar roads & bridges projects in the same district."
      },
      "delay": {
        "score": 13,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 86,
        "flagged": true,
        "reason": "Expenditure of ₹1,029,300 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 8,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00005",
    "workName": "Renovation of Primary School Building, Sector 6",
    "description": "Renovation of Primary School Building, Sector 6 under MPLADS scheme, recommended by Krishan Pal Gurjar, MP for Faridabad.",
    "category": "Education",
    "state": "Haryana",
    "constituency": "Faridabad",
    "mpName": "Krishan Pal Gurjar",
    "authority": "District Rural Development Agency, Faridabad",
    "recommendationDate": "03 Jan 2023",
    "sanctionDate": "14 Mar 2022",
    "sanctionAmount": 18911000,
    "workStage": "Completed",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 17546200,
    "lastExpenditureDate": "07 Aug 2025",
    "risk": {
      "overallScore": 31,
      "level": "LOW",
      "cost": {
        "score": 20,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 34,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 39,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 37,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00006",
    "workName": "Construction of Overhead Water Tank, Block 7",
    "description": "Construction of Overhead Water Tank, Block 7 under MPLADS scheme, recommended by Krishan Pal Gurjar, MP for Faridabad.",
    "category": "Water Supply",
    "state": "Haryana",
    "constituency": "Faridabad",
    "mpName": "Krishan Pal Gurjar",
    "authority": "Municipal Corporation Faridabad",
    "recommendationDate": "17 Jan 2021",
    "sanctionDate": "03 Mar 2022",
    "sanctionAmount": 19016000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 15297700,
    "lastExpenditureDate": "22 Feb 2026",
    "risk": {
      "overallScore": 47,
      "level": "MEDIUM",
      "cost": {
        "score": 46,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 70,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 270 days without progress update."
      },
      "expenditure": {
        "score": 46,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 18,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00007",
    "workName": "Construction of Sub-Health Centre, Sector 5",
    "description": "Construction of Sub-Health Centre, Sector 5 under MPLADS scheme, recommended by Krishan Pal Gurjar, MP for Faridabad.",
    "category": "Health",
    "state": "Haryana",
    "constituency": "Faridabad",
    "mpName": "Krishan Pal Gurjar",
    "authority": "District Panchayat Faridabad",
    "recommendationDate": "17 Apr 2023",
    "sanctionDate": "12 Mar 2023",
    "sanctionAmount": 13932000,
    "workStage": "Delayed",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 3273900,
    "lastExpenditureDate": "12 Apr 2024",
    "risk": {
      "overallScore": 37,
      "level": "LOW",
      "cost": {
        "score": 44,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 43,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 45,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 8,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00008",
    "workName": "Upgradation of Primary Health Centre, Block 20",
    "description": "Upgradation of Primary Health Centre, Block 20 under MPLADS scheme, recommended by Kalyan Vaijinathrao Kale, MP for Jalna.",
    "category": "Health",
    "state": "Maharashtra",
    "constituency": "Jalna",
    "mpName": "Kalyan Vaijinathrao Kale",
    "authority": "Municipal Corporation Jalna",
    "recommendationDate": "14 Nov 2021",
    "sanctionDate": "01 Jan 2023",
    "sanctionAmount": 25283000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 9324200,
    "lastExpenditureDate": "21 Mar 2025",
    "risk": {
      "overallScore": 55,
      "level": "MEDIUM",
      "cost": {
        "score": 86,
        "flagged": true,
        "reason": "The sanctioned amount is 1.9x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 37,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 69,
        "flagged": true,
        "reason": "Expenditure of ₹9,324,200 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 11,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00009",
    "workName": "Construction of Additional Classroom, Govt School Sector 5",
    "description": "Construction of Additional Classroom, Govt School Sector 5 under MPLADS scheme, recommended by Kalyan Vaijinathrao Kale, MP for Jalna.",
    "category": "Education",
    "state": "Maharashtra",
    "constituency": "Jalna",
    "mpName": "Kalyan Vaijinathrao Kale",
    "authority": "Zila Parishad Jalna",
    "recommendationDate": "25 Jun 2021",
    "sanctionDate": "20 Jul 2024",
    "sanctionAmount": 12464000,
    "workStage": "Completed",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 11676400,
    "lastExpenditureDate": "08 Mar 2026",
    "risk": {
      "overallScore": 22,
      "level": "LOW",
      "cost": {
        "score": 21,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 11,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 31,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 28,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00010",
    "workName": "Improvement of Storm Water Drain, Sector 2",
    "description": "Improvement of Storm Water Drain, Sector 2 under MPLADS scheme, recommended by Dr Rani Sri Kumar, MP for Tenkasi(Sc).",
    "category": "Drainage",
    "state": "Tamil Nadu",
    "constituency": "Tenkasi(Sc)",
    "mpName": "Dr Rani Sri Kumar",
    "authority": "Block Development Office, Tenkasi(Sc)",
    "recommendationDate": "11 Jul 2021",
    "sanctionDate": "25 Feb 2023",
    "sanctionAmount": 13441000,
    "workStage": "Completed",
    "vendorName": "M/s Om Construction Co.",
    "totalDisbursed": 12610400,
    "lastExpenditureDate": "21 Jun 2025",
    "risk": {
      "overallScore": 26,
      "level": "LOW",
      "cost": {
        "score": 44,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 11,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 26,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 18,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00011",
    "workName": "Solid Waste Management Unit, Gram 11",
    "description": "Solid Waste Management Unit, Gram 11 under MPLADS scheme, recommended by Dr Rani Sri Kumar, MP for Tenkasi(Sc).",
    "category": "Sanitation",
    "state": "Tamil Nadu",
    "constituency": "Tenkasi(Sc)",
    "mpName": "Dr Rani Sri Kumar",
    "authority": "Zila Parishad Tenkasi(Sc)",
    "recommendationDate": "24 Nov 2023",
    "sanctionDate": "22 Dec 2024",
    "sanctionAmount": 21370000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Om Construction Co.",
    "totalDisbursed": 14727200,
    "lastExpenditureDate": "14 Jun 2024",
    "risk": {
      "overallScore": 83,
      "level": "HIGH",
      "cost": {
        "score": 82,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar sanitation projects in the same district."
      },
      "delay": {
        "score": 84,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 310 days without progress update."
      },
      "expenditure": {
        "score": 91,
        "flagged": true,
        "reason": "Expenditure of ₹14,727,200 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 73,
        "flagged": true,
        "reason": "A similar work description was found in Colony 5, Tamil Nadu, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00012",
    "workName": "Renovation of Primary School Building, Colony 19",
    "description": "Renovation of Primary School Building, Colony 19 under MPLADS scheme, recommended by Chandra Shekhar, MP for Nagina(Sc).",
    "category": "Education",
    "state": "Uttar Pradesh",
    "constituency": "Nagina(Sc)",
    "mpName": "Chandra Shekhar",
    "authority": "Block Development Office, Nagina(Sc)",
    "recommendationDate": "22 Aug 2022",
    "sanctionDate": "16 Sep 2022",
    "sanctionAmount": 17498000,
    "workStage": "Completed",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 16947400,
    "lastExpenditureDate": "22 Mar 2026",
    "risk": {
      "overallScore": 79,
      "level": "HIGH",
      "cost": {
        "score": 92,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 80,
        "flagged": true,
        "reason": "Project has remained in the 'Completed' stage for more than 240 days without progress update."
      },
      "expenditure": {
        "score": 77,
        "flagged": true,
        "reason": "Expenditure of ₹16,947,400 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 57,
        "flagged": true,
        "reason": "A similar work description was found in Panchayat 16, Uttar Pradesh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00013",
    "workName": "Construction of Drainage System, Sector 14",
    "description": "Construction of Drainage System, Sector 14 under MPLADS scheme, recommended by Chandra Shekhar, MP for Nagina(Sc).",
    "category": "Drainage",
    "state": "Uttar Pradesh",
    "constituency": "Nagina(Sc)",
    "mpName": "Chandra Shekhar",
    "authority": "District Rural Development Agency, Nagina(Sc)",
    "recommendationDate": "08 Jul 2021",
    "sanctionDate": "17 Dec 2022",
    "sanctionAmount": 22290000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 18738500,
    "lastExpenditureDate": "18 Jan 2025",
    "risk": {
      "overallScore": 52,
      "level": "MEDIUM",
      "cost": {
        "score": 39,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 85,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 270 days without progress update."
      },
      "expenditure": {
        "score": 42,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 37,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00014",
    "workName": "Construction of Sub-Health Centre, Panchayat 21",
    "description": "Construction of Sub-Health Centre, Panchayat 21 under MPLADS scheme, recommended by Chandra Shekhar, MP for Nagina(Sc).",
    "category": "Health",
    "state": "Uttar Pradesh",
    "constituency": "Nagina(Sc)",
    "mpName": "Chandra Shekhar",
    "authority": "District Rural Development Agency, Nagina(Sc)",
    "recommendationDate": "03 Sep 2022",
    "sanctionDate": "08 Mar 2022",
    "sanctionAmount": 19318000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 12114700,
    "lastExpenditureDate": "05 Dec 2025",
    "risk": {
      "overallScore": 54,
      "level": "MEDIUM",
      "cost": {
        "score": 85,
        "flagged": true,
        "reason": "The sanctioned amount is 1.7x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 68,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 34,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 3,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00015",
    "workName": "Upgradation of Primary Health Centre, Sector 14",
    "description": "Upgradation of Primary Health Centre, Sector 14 under MPLADS scheme, recommended by Bibhu Prasad Tarai, MP for Jagatsinghpur(Sc).",
    "category": "Health",
    "state": "Odisha",
    "constituency": "Jagatsinghpur(Sc)",
    "mpName": "Bibhu Prasad Tarai",
    "authority": "Municipal Corporation Jagatsinghpur(Sc)",
    "recommendationDate": "20 Mar 2022",
    "sanctionDate": "13 Jan 2024",
    "sanctionAmount": 19551000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 8308900,
    "lastExpenditureDate": "22 Oct 2026",
    "risk": {
      "overallScore": 82,
      "level": "HIGH",
      "cost": {
        "score": 76,
        "flagged": true,
        "reason": "The sanctioned amount is 2.2x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 81,
        "flagged": true,
        "reason": "Project has remained in the 'Work in Progress' stage for more than 270 days without progress update."
      },
      "expenditure": {
        "score": 94,
        "flagged": true,
        "reason": "Expenditure of ₹8,308,900 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 79,
        "flagged": true,
        "reason": "A similar work description was found in Block 14, Odisha, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00016",
    "workName": "Village Street Light Improvement, Ward No. 24",
    "description": "Village Street Light Improvement, Ward No. 24 under MPLADS scheme, recommended by Bibhu Prasad Tarai, MP for Jagatsinghpur(Sc).",
    "category": "Others",
    "state": "Odisha",
    "constituency": "Jagatsinghpur(Sc)",
    "mpName": "Bibhu Prasad Tarai",
    "authority": "Block Development Office, Jagatsinghpur(Sc)",
    "recommendationDate": "27 Apr 2021",
    "sanctionDate": "05 Oct 2022",
    "sanctionAmount": 7501000,
    "workStage": "Delayed",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 1581700,
    "lastExpenditureDate": "16 Mar 2024",
    "risk": {
      "overallScore": 37,
      "level": "LOW",
      "cost": {
        "score": 23,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 88,
        "flagged": true,
        "reason": "Project has remained in the 'Delayed' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 17,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 12,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00017",
    "workName": "Construction of Community Hall, Sector 23",
    "description": "Construction of Community Hall, Sector 23 under MPLADS scheme, recommended by Shri  Dharambir Singh, MP for Bhiwani Mahendragarh.",
    "category": "Community Infrastructure",
    "state": "Haryana",
    "constituency": "Bhiwani Mahendragarh",
    "mpName": "Shri  Dharambir Singh",
    "authority": "District Rural Development Agency, Bhiwani Mahendragarh",
    "recommendationDate": "26 Oct 2021",
    "sanctionDate": "18 Jun 2022",
    "sanctionAmount": 9249000,
    "workStage": "Completed",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 9138200,
    "lastExpenditureDate": "12 Nov 2025",
    "risk": {
      "overallScore": 44,
      "level": "MEDIUM",
      "cost": {
        "score": 72,
        "flagged": true,
        "reason": "The sanctioned amount is 2.2x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 16,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 50,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 31,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00018",
    "workName": "Construction of Sub-Health Centre, Colony 18",
    "description": "Construction of Sub-Health Centre, Colony 18 under MPLADS scheme, recommended by Shri  Dharambir Singh, MP for Bhiwani Mahendragarh.",
    "category": "Health",
    "state": "Haryana",
    "constituency": "Bhiwani Mahendragarh",
    "mpName": "Shri  Dharambir Singh",
    "authority": "Zila Parishad Bhiwani Mahendragarh",
    "recommendationDate": "25 Apr 2022",
    "sanctionDate": "20 Oct 2023",
    "sanctionAmount": 17774000,
    "workStage": "Completed",
    "vendorName": "M/s Kisan Infra Developers",
    "totalDisbursed": 17681000,
    "lastExpenditureDate": "11 Jul 2026",
    "risk": {
      "overallScore": 54,
      "level": "MEDIUM",
      "cost": {
        "score": 21,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 81,
        "flagged": true,
        "reason": "Project has remained in the 'Completed' stage for more than 240 days without progress update."
      },
      "expenditure": {
        "score": 82,
        "flagged": true,
        "reason": "Expenditure of ₹17,681,000 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 35,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00019",
    "workName": "Village Street Light Improvement, Colony 8",
    "description": "Village Street Light Improvement, Colony 8 under MPLADS scheme, recommended by Andrew J. Syngkon, MP for Shillong.",
    "category": "Others",
    "state": "Meghalaya",
    "constituency": "Shillong",
    "mpName": "Andrew J. Syngkon",
    "authority": "Zila Parishad Shillong",
    "recommendationDate": "12 Oct 2023",
    "sanctionDate": "17 Sep 2023",
    "sanctionAmount": 12832000,
    "workStage": "Completed",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 12220600,
    "lastExpenditureDate": "24 Jul 2025",
    "risk": {
      "overallScore": 44,
      "level": "MEDIUM",
      "cost": {
        "score": 39,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 26,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 77,
        "flagged": true,
        "reason": "Expenditure of ₹12,220,600 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 36,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00020",
    "workName": "Village Street Light Improvement, Block 24",
    "description": "Village Street Light Improvement, Block 24 under MPLADS scheme, recommended by Andrew J. Syngkon, MP for Shillong.",
    "category": "Others",
    "state": "Meghalaya",
    "constituency": "Shillong",
    "mpName": "Andrew J. Syngkon",
    "authority": "District Rural Development Agency, Shillong",
    "recommendationDate": "18 Dec 2021",
    "sanctionDate": "02 May 2022",
    "sanctionAmount": 18398000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 12288800,
    "lastExpenditureDate": "10 Sep 2024",
    "risk": {
      "overallScore": 61,
      "level": "MEDIUM",
      "cost": {
        "score": 99,
        "flagged": true,
        "reason": "The sanctioned amount is 2.1x higher than similar others projects in the same district."
      },
      "delay": {
        "score": 65,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 310 days without progress update."
      },
      "expenditure": {
        "score": 40,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 13,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00021",
    "workName": "Construction of Drainage System, Sector 16",
    "description": "Construction of Drainage System, Sector 16 under MPLADS scheme, recommended by Andrew J. Syngkon, MP for Shillong.",
    "category": "Drainage",
    "state": "Meghalaya",
    "constituency": "Shillong",
    "mpName": "Andrew J. Syngkon",
    "authority": "Zila Parishad Shillong",
    "recommendationDate": "20 Jul 2023",
    "sanctionDate": "08 Oct 2024",
    "sanctionAmount": 9888000,
    "workStage": "Completed",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 9164300,
    "lastExpenditureDate": "15 Jul 2026",
    "risk": {
      "overallScore": 49,
      "level": "MEDIUM",
      "cost": {
        "score": 90,
        "flagged": true,
        "reason": "The sanctioned amount is 2.3x higher than similar drainage projects in the same district."
      },
      "delay": {
        "score": 29,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 49,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 8,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00022",
    "workName": "Construction of School Boundary Wall, Panchayat 6",
    "description": "Construction of School Boundary Wall, Panchayat 6 under MPLADS scheme, recommended by Ananta Nayak, MP for Keonjhar(St).",
    "category": "Education",
    "state": "Odisha",
    "constituency": "Keonjhar(St)",
    "mpName": "Ananta Nayak",
    "authority": "Block Development Office, Keonjhar(St)",
    "recommendationDate": "03 Aug 2023",
    "sanctionDate": "09 Apr 2024",
    "sanctionAmount": 9226000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 623500,
    "lastExpenditureDate": "22 Oct 2026",
    "risk": {
      "overallScore": 46,
      "level": "MEDIUM",
      "cost": {
        "score": 75,
        "flagged": true,
        "reason": "The sanctioned amount is 1.9x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 19,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 14,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 74,
        "flagged": true,
        "reason": "A similar work description was found in Colony 24, Odisha, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00023",
    "workName": "Improvement of Storm Water Drain, Sector 23",
    "description": "Improvement of Storm Water Drain, Sector 23 under MPLADS scheme, recommended by Brijmohan Agrawal, MP for Raipur.",
    "category": "Drainage",
    "state": "Chhattisgarh",
    "constituency": "Raipur",
    "mpName": "Brijmohan Agrawal",
    "authority": "District Rural Development Agency, Raipur",
    "recommendationDate": "09 Oct 2022",
    "sanctionDate": "08 Feb 2022",
    "sanctionAmount": 25980000,
    "workStage": "Delayed",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 9124400,
    "lastExpenditureDate": "19 Oct 2026",
    "risk": {
      "overallScore": 25,
      "level": "LOW",
      "cost": {
        "score": 27,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 21,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 38,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 13,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00024",
    "workName": "Construction of Crematorium Shed, Block 14",
    "description": "Construction of Crematorium Shed, Block 14 under MPLADS scheme, recommended by Brijmohan Agrawal, MP for Raipur.",
    "category": "Others",
    "state": "Chhattisgarh",
    "constituency": "Raipur",
    "mpName": "Brijmohan Agrawal",
    "authority": "District Panchayat Raipur",
    "recommendationDate": "15 Jan 2023",
    "sanctionDate": "09 Jun 2022",
    "sanctionAmount": 13364000,
    "workStage": "Work in Progress",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 5816600,
    "lastExpenditureDate": "25 Feb 2025",
    "risk": {
      "overallScore": 26,
      "level": "LOW",
      "cost": {
        "score": 10,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 44,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 22,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 33,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00025",
    "workName": "Construction of Sub-Health Centre, Colony 5",
    "description": "Construction of Sub-Health Centre, Colony 5 under MPLADS scheme, recommended by Brijmohan Agrawal, MP for Raipur.",
    "category": "Health",
    "state": "Chhattisgarh",
    "constituency": "Raipur",
    "mpName": "Brijmohan Agrawal",
    "authority": "Zila Parishad Raipur",
    "recommendationDate": "18 Jan 2023",
    "sanctionDate": "08 Feb 2023",
    "sanctionAmount": 14243000,
    "workStage": "Completed",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 13376200,
    "lastExpenditureDate": "04 Aug 2024",
    "risk": {
      "overallScore": 53,
      "level": "MEDIUM",
      "cost": {
        "score": 94,
        "flagged": true,
        "reason": "The sanctioned amount is 1.7x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 27,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 40,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 37,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00026",
    "workName": "Improvement of Storm Water Drain, Block 14",
    "description": "Improvement of Storm Water Drain, Block 14 under MPLADS scheme, recommended by Kalanidhi Veeraswamy, MP for Chennai North.",
    "category": "Drainage",
    "state": "Tamil Nadu",
    "constituency": "Chennai North",
    "mpName": "Kalanidhi Veeraswamy",
    "authority": "District Rural Development Agency, Chennai North",
    "recommendationDate": "15 Mar 2022",
    "sanctionDate": "12 Aug 2024",
    "sanctionAmount": 35813000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 25230100,
    "lastExpenditureDate": "25 Sep 2025",
    "risk": {
      "overallScore": 40,
      "level": "MEDIUM",
      "cost": {
        "score": 30,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 25,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 36,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 85,
        "flagged": true,
        "reason": "A similar work description was found in Gram 13, Tamil Nadu, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00027",
    "workName": "Construction of Additional Classroom, Govt School Sector 2",
    "description": "Construction of Additional Classroom, Govt School Sector 2 under MPLADS scheme, recommended by Kalanidhi Veeraswamy, MP for Chennai North.",
    "category": "Education",
    "state": "Tamil Nadu",
    "constituency": "Chennai North",
    "mpName": "Kalanidhi Veeraswamy",
    "authority": "Block Development Office, Chennai North",
    "recommendationDate": "14 Mar 2023",
    "sanctionDate": "03 Mar 2024",
    "sanctionAmount": 18371000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 13853700,
    "lastExpenditureDate": "11 May 2025",
    "risk": {
      "overallScore": 34,
      "level": "LOW",
      "cost": {
        "score": 15,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 44,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 50,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 33,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00028",
    "workName": "Upgradation of Primary Health Centre, Panchayat 24",
    "description": "Upgradation of Primary Health Centre, Panchayat 24 under MPLADS scheme, recommended by Kartick Chandra Paul, MP for Raiganj.",
    "category": "Health",
    "state": "West Bengal",
    "constituency": "Raiganj",
    "mpName": "Kartick Chandra Paul",
    "authority": "Zila Parishad Raiganj",
    "recommendationDate": "26 Jun 2021",
    "sanctionDate": "12 May 2022",
    "sanctionAmount": 25086000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 2384700,
    "lastExpenditureDate": "05 Jul 2025",
    "risk": {
      "overallScore": 28,
      "level": "LOW",
      "cost": {
        "score": 21,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 15,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 49,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 33,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00029",
    "workName": "Upgradation of Primary Health Centre, Sector 9",
    "description": "Upgradation of Primary Health Centre, Sector 9 under MPLADS scheme, recommended by Kartick Chandra Paul, MP for Raiganj.",
    "category": "Health",
    "state": "West Bengal",
    "constituency": "Raiganj",
    "mpName": "Kartick Chandra Paul",
    "authority": "District Panchayat Raiganj",
    "recommendationDate": "14 Nov 2022",
    "sanctionDate": "15 May 2024",
    "sanctionAmount": 36018000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 22541900,
    "lastExpenditureDate": "13 Apr 2025",
    "risk": {
      "overallScore": 64,
      "level": "MEDIUM",
      "cost": {
        "score": 84,
        "flagged": true,
        "reason": "The sanctioned amount is 1.9x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 83,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 185 days without progress update."
      },
      "expenditure": {
        "score": 35,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 38,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00030",
    "workName": "Construction of Sub-Health Centre, Panchayat 20",
    "description": "Construction of Sub-Health Centre, Panchayat 20 under MPLADS scheme, recommended by Ummeda Ram Beniwal, MP for Barmer.",
    "category": "Health",
    "state": "Rajasthan",
    "constituency": "Barmer",
    "mpName": "Ummeda Ram Beniwal",
    "authority": "District Rural Development Agency, Barmer",
    "recommendationDate": "21 Nov 2021",
    "sanctionDate": "26 May 2022",
    "sanctionAmount": 12823000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 7565700,
    "lastExpenditureDate": "19 Jan 2025",
    "risk": {
      "overallScore": 59,
      "level": "MEDIUM",
      "cost": {
        "score": 81,
        "flagged": true,
        "reason": "The sanctioned amount is 1.7x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 36,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 88,
        "flagged": true,
        "reason": "Expenditure of ₹7,565,700 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 19,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00031",
    "workName": "Upgradation of Primary Health Centre, Gram 11",
    "description": "Upgradation of Primary Health Centre, Gram 11 under MPLADS scheme, recommended by Ummeda Ram Beniwal, MP for Barmer.",
    "category": "Health",
    "state": "Rajasthan",
    "constituency": "Barmer",
    "mpName": "Ummeda Ram Beniwal",
    "authority": "Zila Parishad Barmer",
    "recommendationDate": "03 Jun 2023",
    "sanctionDate": "09 Jan 2023",
    "sanctionAmount": 17392000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 1967400,
    "lastExpenditureDate": "15 Feb 2026",
    "risk": {
      "overallScore": 47,
      "level": "MEDIUM",
      "cost": {
        "score": 26,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 50,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 79,
        "flagged": true,
        "reason": "Expenditure of ₹1,967,400 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 37,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00032",
    "workName": "Improvement of Storm Water Drain, Gram 15",
    "description": "Improvement of Storm Water Drain, Gram 15 under MPLADS scheme, recommended by Ummeda Ram Beniwal, MP for Barmer.",
    "category": "Drainage",
    "state": "Rajasthan",
    "constituency": "Barmer",
    "mpName": "Ummeda Ram Beniwal",
    "authority": "District Rural Development Agency, Barmer",
    "recommendationDate": "13 Mar 2023",
    "sanctionDate": "22 Jun 2023",
    "sanctionAmount": 18729000,
    "workStage": "Work in Progress",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 4995900,
    "lastExpenditureDate": "18 Dec 2026",
    "risk": {
      "overallScore": 31,
      "level": "LOW",
      "cost": {
        "score": 19,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 16,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 27,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 78,
        "flagged": true,
        "reason": "A similar work description was found in Panchayat 15, Rajasthan, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00033",
    "workName": "Improvement of Storm Water Drain, Gram 12",
    "description": "Improvement of Storm Water Drain, Gram 12 under MPLADS scheme, recommended by Amrinder Singh Raja Warring, MP for Ludhiana.",
    "category": "Drainage",
    "state": "Punjab",
    "constituency": "Ludhiana",
    "mpName": "Amrinder Singh Raja Warring",
    "authority": "Municipal Corporation Ludhiana",
    "recommendationDate": "01 Oct 2023",
    "sanctionDate": "08 Jun 2022",
    "sanctionAmount": 8863000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 6000700,
    "lastExpenditureDate": "07 Oct 2024",
    "risk": {
      "overallScore": 36,
      "level": "LOW",
      "cost": {
        "score": 23,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 24,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 48,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 64,
        "flagged": true,
        "reason": "A similar work description was found in Panchayat 18, Punjab, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00034",
    "workName": "Construction of Additional Classroom, Govt School Ward No. 22",
    "description": "Construction of Additional Classroom, Govt School Ward No. 22 under MPLADS scheme, recommended by Amrinder Singh Raja Warring, MP for Ludhiana.",
    "category": "Education",
    "state": "Punjab",
    "constituency": "Ludhiana",
    "mpName": "Amrinder Singh Raja Warring",
    "authority": "District Panchayat Ludhiana",
    "recommendationDate": "04 Sep 2022",
    "sanctionDate": "16 Feb 2024",
    "sanctionAmount": 10002000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 5150900,
    "lastExpenditureDate": "17 Jun 2025",
    "risk": {
      "overallScore": 29,
      "level": "LOW",
      "cost": {
        "score": 24,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 12,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 11,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 85,
        "flagged": true,
        "reason": "A similar work description was found in Sector 14, Punjab, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00035",
    "workName": "Construction of Drainage System, Ward No. 11",
    "description": "Construction of Drainage System, Ward No. 11 under MPLADS scheme, recommended by Janardan Mishra, MP for Rewa.",
    "category": "Drainage",
    "state": "Madhya Pradesh",
    "constituency": "Rewa",
    "mpName": "Janardan Mishra",
    "authority": "District Panchayat Rewa",
    "recommendationDate": "20 Sep 2022",
    "sanctionDate": "26 Feb 2023",
    "sanctionAmount": 8991000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Ganga Infrastructure Pvt. Ltd.",
    "totalDisbursed": 4466400,
    "lastExpenditureDate": "28 Feb 2026",
    "risk": {
      "overallScore": 32,
      "level": "LOW",
      "cost": {
        "score": 45,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 23,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 24,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 31,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00036",
    "workName": "Renovation of Panchayat Bhawan, Block 22",
    "description": "Renovation of Panchayat Bhawan, Block 22 under MPLADS scheme, recommended by Janardan Mishra, MP for Rewa.",
    "category": "Community Infrastructure",
    "state": "Madhya Pradesh",
    "constituency": "Rewa",
    "mpName": "Janardan Mishra",
    "authority": "Zila Parishad Rewa",
    "recommendationDate": "26 Jun 2023",
    "sanctionDate": "02 Sep 2022",
    "sanctionAmount": 15682000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 4394300,
    "lastExpenditureDate": "18 Sep 2026",
    "risk": {
      "overallScore": 49,
      "level": "MEDIUM",
      "cost": {
        "score": 83,
        "flagged": true,
        "reason": "The sanctioned amount is 2.2x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 37,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 48,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 8,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00037",
    "workName": "Construction of Crematorium Shed, Panchayat 4",
    "description": "Construction of Crematorium Shed, Panchayat 4 under MPLADS scheme, recommended by Janardan Mishra, MP for Rewa.",
    "category": "Others",
    "state": "Madhya Pradesh",
    "constituency": "Rewa",
    "mpName": "Janardan Mishra",
    "authority": "District Panchayat Rewa",
    "recommendationDate": "22 Oct 2023",
    "sanctionDate": "01 Sep 2024",
    "sanctionAmount": 23696000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 12045700,
    "lastExpenditureDate": "27 Nov 2026",
    "risk": {
      "overallScore": 45,
      "level": "MEDIUM",
      "cost": {
        "score": 80,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar others projects in the same district."
      },
      "delay": {
        "score": 29,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 21,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 38,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00038",
    "workName": "Construction of Drainage System, Gram 17",
    "description": "Construction of Drainage System, Gram 17 under MPLADS scheme, recommended by Shobha Karandlaje, MP for Bangalore North.",
    "category": "Drainage",
    "state": "Karnataka",
    "constituency": "Bangalore North",
    "mpName": "Shobha Karandlaje",
    "authority": "Municipal Corporation Bangalore North",
    "recommendationDate": "06 Mar 2021",
    "sanctionDate": "22 Jan 2024",
    "sanctionAmount": 16751000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 11952400,
    "lastExpenditureDate": "15 May 2024",
    "risk": {
      "overallScore": 48,
      "level": "MEDIUM",
      "cost": {
        "score": 38,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 97,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 185 days without progress update."
      },
      "expenditure": {
        "score": 17,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 33,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00039",
    "workName": "Construction of Community Hall, Colony 2",
    "description": "Construction of Community Hall, Colony 2 under MPLADS scheme, recommended by Kali Charan Singh, MP for Chatra.",
    "category": "Community Infrastructure",
    "state": "Jharkhand",
    "constituency": "Chatra",
    "mpName": "Kali Charan Singh",
    "authority": "District Rural Development Agency, Chatra",
    "recommendationDate": "05 Mar 2022",
    "sanctionDate": "23 Sep 2023",
    "sanctionAmount": 12459000,
    "workStage": "Delayed",
    "vendorName": "M/s Kisan Infra Developers",
    "totalDisbursed": 4660700,
    "lastExpenditureDate": "18 Sep 2024",
    "risk": {
      "overallScore": 25,
      "level": "LOW",
      "cost": {
        "score": 14,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 37,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 14,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 38,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00040",
    "workName": "Renovation of Panchayat Bhawan, Block 4",
    "description": "Renovation of Panchayat Bhawan, Block 4 under MPLADS scheme, recommended by Kali Charan Singh, MP for Chatra.",
    "category": "Community Infrastructure",
    "state": "Jharkhand",
    "constituency": "Chatra",
    "mpName": "Kali Charan Singh",
    "authority": "Zila Parishad Chatra",
    "recommendationDate": "14 Apr 2021",
    "sanctionDate": "17 Jul 2024",
    "sanctionAmount": 7204000,
    "workStage": "Work in Progress",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 3804800,
    "lastExpenditureDate": "28 Jul 2024",
    "risk": {
      "overallScore": 28,
      "level": "LOW",
      "cost": {
        "score": 31,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 14,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 43,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 24,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00041",
    "workName": "Construction of Additional Classroom, Govt School Block 7",
    "description": "Construction of Additional Classroom, Govt School Block 7 under MPLADS scheme, recommended by Shri Sarbananda Sonowal (18Ls), MP for Dibrugarh.",
    "category": "Education",
    "state": "Assam",
    "constituency": "Dibrugarh",
    "mpName": "Shri Sarbananda Sonowal (18Ls)",
    "authority": "District Rural Development Agency, Dibrugarh",
    "recommendationDate": "22 Aug 2023",
    "sanctionDate": "21 Nov 2024",
    "sanctionAmount": 22404000,
    "workStage": "Completed",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 21497300,
    "lastExpenditureDate": "28 Jun 2026",
    "risk": {
      "overallScore": 49,
      "level": "MEDIUM",
      "cost": {
        "score": 38,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 38,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 47,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 87,
        "flagged": true,
        "reason": "A similar work description was found in Ward No. 10, Assam, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00042",
    "workName": "Construction of CC Road at Block 10",
    "description": "Construction of CC Road at Block 10 under MPLADS scheme, recommended by Manoj Tiwari, MP for North East Delhi.",
    "category": "Roads & Bridges",
    "state": "Delhi",
    "constituency": "North East Delhi",
    "mpName": "Manoj Tiwari",
    "authority": "Block Development Office, North East Delhi",
    "recommendationDate": "15 Jan 2023",
    "sanctionDate": "07 Nov 2024",
    "sanctionAmount": 36043000,
    "workStage": "Delayed",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 19246300,
    "lastExpenditureDate": "16 Oct 2025",
    "risk": {
      "overallScore": 40,
      "level": "MEDIUM",
      "cost": {
        "score": 38,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 31,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 21,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 83,
        "flagged": true,
        "reason": "A similar work description was found in Sector 17, Delhi, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00043",
    "workName": "Solid Waste Management Unit, Block 10",
    "description": "Solid Waste Management Unit, Block 10 under MPLADS scheme, recommended by Aditya Yadav, MP for Badaun.",
    "category": "Sanitation",
    "state": "Uttar Pradesh",
    "constituency": "Badaun",
    "mpName": "Aditya Yadav",
    "authority": "Zila Parishad Badaun",
    "recommendationDate": "10 Jul 2023",
    "sanctionDate": "28 Dec 2023",
    "sanctionAmount": 17565000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 10629500,
    "lastExpenditureDate": "28 Oct 2026",
    "risk": {
      "overallScore": 84,
      "level": "HIGH",
      "cost": {
        "score": 93,
        "flagged": true,
        "reason": "The sanctioned amount is 1.5x higher than similar sanitation projects in the same district."
      },
      "delay": {
        "score": 90,
        "flagged": true,
        "reason": "Project has remained in the 'Work in Progress' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 70,
        "flagged": true,
        "reason": "Expenditure of ₹10,629,500 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 79,
        "flagged": true,
        "reason": "A similar work description was found in Gram 11, Uttar Pradesh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00044",
    "workName": "Improvement of Storm Water Drain, Gram 22",
    "description": "Improvement of Storm Water Drain, Gram 22 under MPLADS scheme, recommended by Aditya Yadav, MP for Badaun.",
    "category": "Drainage",
    "state": "Uttar Pradesh",
    "constituency": "Badaun",
    "mpName": "Aditya Yadav",
    "authority": "Zila Parishad Badaun",
    "recommendationDate": "03 Mar 2021",
    "sanctionDate": "17 Feb 2023",
    "sanctionAmount": 17661000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 818200,
    "lastExpenditureDate": "17 Dec 2026",
    "risk": {
      "overallScore": 69,
      "level": "MEDIUM",
      "cost": {
        "score": 96,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar drainage projects in the same district."
      },
      "delay": {
        "score": 74,
        "flagged": true,
        "reason": "Project has remained in the 'Sanctioned' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 75,
        "flagged": true,
        "reason": "Expenditure of ₹818,200 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 4,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00045",
    "workName": "Installation of Solar Street Lights, Panchayat 18",
    "description": "Installation of Solar Street Lights, Panchayat 18 under MPLADS scheme, recommended by Dushyant Singh, MP for Jhalawar-Baran.",
    "category": "Others",
    "state": "Rajasthan",
    "constituency": "Jhalawar-Baran",
    "mpName": "Dushyant Singh",
    "authority": "District Panchayat Jhalawar-Baran",
    "recommendationDate": "25 May 2022",
    "sanctionDate": "17 Sep 2023",
    "sanctionAmount": 15084000,
    "workStage": "Completed",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 15020200,
    "lastExpenditureDate": "27 Mar 2025",
    "risk": {
      "overallScore": 29,
      "level": "LOW",
      "cost": {
        "score": 26,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 40,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 16,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 35,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00046",
    "workName": "Construction of School Boundary Wall, Block 15",
    "description": "Construction of School Boundary Wall, Block 15 under MPLADS scheme, recommended by Dushyant Singh, MP for Jhalawar-Baran.",
    "category": "Education",
    "state": "Rajasthan",
    "constituency": "Jhalawar-Baran",
    "mpName": "Dushyant Singh",
    "authority": "District Panchayat Jhalawar-Baran",
    "recommendationDate": "17 Jul 2021",
    "sanctionDate": "13 Apr 2023",
    "sanctionAmount": 9900000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 7503200,
    "lastExpenditureDate": "08 Jun 2024",
    "risk": {
      "overallScore": 42,
      "level": "MEDIUM",
      "cost": {
        "score": 31,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 83,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 270 days without progress update."
      },
      "expenditure": {
        "score": 18,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 32,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00047",
    "workName": "Construction of Sub-Health Centre, Panchayat 5",
    "description": "Construction of Sub-Health Centre, Panchayat 5 under MPLADS scheme, recommended by Rabindra Narayan Behera, MP for Jajpur(Sc).",
    "category": "Health",
    "state": "Odisha",
    "constituency": "Jajpur(Sc)",
    "mpName": "Rabindra Narayan Behera",
    "authority": "Block Development Office, Jajpur(Sc)",
    "recommendationDate": "20 Aug 2021",
    "sanctionDate": "21 Jan 2024",
    "sanctionAmount": 10133000,
    "workStage": "Work in Progress",
    "vendorName": "M/s United Builders & Co.",
    "totalDisbursed": 2751000,
    "lastExpenditureDate": "08 Oct 2026",
    "risk": {
      "overallScore": 38,
      "level": "LOW",
      "cost": {
        "score": 72,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 25,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 15,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 25,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00048",
    "workName": "Construction of Village Haat/Market Shed, Sector 2",
    "description": "Construction of Village Haat/Market Shed, Sector 2 under MPLADS scheme, recommended by Dr.Mallu Ravi, MP for Nagarkurnool(Sc).",
    "category": "Community Infrastructure",
    "state": "Telangana",
    "constituency": "Nagarkurnool(Sc)",
    "mpName": "Dr.Mallu Ravi",
    "authority": "Zila Parishad Nagarkurnool(Sc)",
    "recommendationDate": "24 Oct 2021",
    "sanctionDate": "02 Mar 2023",
    "sanctionAmount": 17018000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 6989200,
    "lastExpenditureDate": "11 Sep 2025",
    "risk": {
      "overallScore": 50,
      "level": "MEDIUM",
      "cost": {
        "score": 96,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 40,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 14,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 31,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00049",
    "workName": "Widening of Approach Road, Block 10",
    "description": "Widening of Approach Road, Block 10 under MPLADS scheme, recommended by Kadiyam Kavya, MP for Warangel(Sc).",
    "category": "Roads & Bridges",
    "state": "Telangana",
    "constituency": "Warangel(Sc)",
    "mpName": "Kadiyam Kavya",
    "authority": "Municipal Corporation Warangel(Sc)",
    "recommendationDate": "09 Jun 2023",
    "sanctionDate": "14 Jun 2022",
    "sanctionAmount": 32068000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 21385700,
    "lastExpenditureDate": "15 Dec 2025",
    "risk": {
      "overallScore": 35,
      "level": "LOW",
      "cost": {
        "score": 21,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 82,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 185 days without progress update."
      },
      "expenditure": {
        "score": 15,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 13,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00050",
    "workName": "Improvement of Storm Water Drain, Block 22",
    "description": "Improvement of Storm Water Drain, Block 22 under MPLADS scheme, recommended by Kadiyam Kavya, MP for Warangel(Sc).",
    "category": "Drainage",
    "state": "Telangana",
    "constituency": "Warangel(Sc)",
    "mpName": "Kadiyam Kavya",
    "authority": "Municipal Corporation Warangel(Sc)",
    "recommendationDate": "14 Oct 2022",
    "sanctionDate": "26 Nov 2023",
    "sanctionAmount": 11735000,
    "workStage": "Completed",
    "vendorName": "M/s Ganga Infrastructure Pvt. Ltd.",
    "totalDisbursed": 10836000,
    "lastExpenditureDate": "22 Feb 2024",
    "risk": {
      "overallScore": 31,
      "level": "LOW",
      "cost": {
        "score": 20,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 19,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 38,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 59,
        "flagged": true,
        "reason": "A similar work description was found in Panchayat 21, Telangana, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00051",
    "workName": "Widening of Approach Road, Colony 5",
    "description": "Widening of Approach Road, Colony 5 under MPLADS scheme, recommended by Prof Sp Singh Baghel, MP for Agra(Sc).",
    "category": "Roads & Bridges",
    "state": "Uttar Pradesh",
    "constituency": "Agra(Sc)",
    "mpName": "Prof Sp Singh Baghel",
    "authority": "Municipal Corporation Agra(Sc)",
    "recommendationDate": "01 Feb 2021",
    "sanctionDate": "16 Mar 2024",
    "sanctionAmount": 31061000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 15787200,
    "lastExpenditureDate": "18 Jul 2026",
    "risk": {
      "overallScore": 59,
      "level": "MEDIUM",
      "cost": {
        "score": 38,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 96,
        "flagged": true,
        "reason": "Project has remained in the 'Work in Progress' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 69,
        "flagged": true,
        "reason": "Expenditure of ₹15,787,200 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 30,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00052",
    "workName": "Solid Waste Management Unit, Gram 3",
    "description": "Solid Waste Management Unit, Gram 3 under MPLADS scheme, recommended by Prof Sp Singh Baghel, MP for Agra(Sc).",
    "category": "Sanitation",
    "state": "Uttar Pradesh",
    "constituency": "Agra(Sc)",
    "mpName": "Prof Sp Singh Baghel",
    "authority": "Zila Parishad Agra(Sc)",
    "recommendationDate": "26 Apr 2021",
    "sanctionDate": "26 Apr 2022",
    "sanctionAmount": 23365000,
    "workStage": "Completed",
    "vendorName": "M/s Ganga Infrastructure Pvt. Ltd.",
    "totalDisbursed": 22979400,
    "lastExpenditureDate": "12 Jan 2025",
    "risk": {
      "overallScore": 33,
      "level": "LOW",
      "cost": {
        "score": 45,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 15,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 40,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 28,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00053",
    "workName": "Improvement of Storm Water Drain, Sector 15",
    "description": "Improvement of Storm Water Drain, Sector 15 under MPLADS scheme, recommended by Prof Sp Singh Baghel, MP for Agra(Sc).",
    "category": "Drainage",
    "state": "Uttar Pradesh",
    "constituency": "Agra(Sc)",
    "mpName": "Prof Sp Singh Baghel",
    "authority": "District Panchayat Agra(Sc)",
    "recommendationDate": "17 Feb 2021",
    "sanctionDate": "06 May 2022",
    "sanctionAmount": 6648000,
    "workStage": "Completed",
    "vendorName": "M/s United Builders & Co.",
    "totalDisbursed": 6184800,
    "lastExpenditureDate": "23 Jun 2024",
    "risk": {
      "overallScore": 50,
      "level": "MEDIUM",
      "cost": {
        "score": 43,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 15,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 82,
        "flagged": true,
        "reason": "Expenditure of ₹6,184,800 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 74,
        "flagged": true,
        "reason": "A similar work description was found in Colony 18, Uttar Pradesh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00054",
    "workName": "Construction of School Boundary Wall, Panchayat 22",
    "description": "Construction of School Boundary Wall, Panchayat 22 under MPLADS scheme, recommended by Brijendra Singh Ola, MP for Jhunjhunu.",
    "category": "Education",
    "state": "Rajasthan",
    "constituency": "Jhunjhunu",
    "mpName": "Brijendra Singh Ola",
    "authority": "Zila Parishad Jhunjhunu",
    "recommendationDate": "09 Oct 2023",
    "sanctionDate": "25 Apr 2024",
    "sanctionAmount": 25359000,
    "workStage": "Completed",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 23387800,
    "lastExpenditureDate": "20 Jul 2026",
    "risk": {
      "overallScore": 46,
      "level": "MEDIUM",
      "cost": {
        "score": 50,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 29,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 90,
        "flagged": true,
        "reason": "Expenditure of ₹23,387,800 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 6,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00055",
    "workName": "Construction of Community Hall, Sector 15",
    "description": "Construction of Community Hall, Sector 15 under MPLADS scheme, recommended by Brijendra Singh Ola, MP for Jhunjhunu.",
    "category": "Community Infrastructure",
    "state": "Rajasthan",
    "constituency": "Jhunjhunu",
    "mpName": "Brijendra Singh Ola",
    "authority": "Zila Parishad Jhunjhunu",
    "recommendationDate": "18 Sep 2022",
    "sanctionDate": "08 Jun 2022",
    "sanctionAmount": 13117000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 5164100,
    "lastExpenditureDate": "09 Feb 2025",
    "risk": {
      "overallScore": 44,
      "level": "MEDIUM",
      "cost": {
        "score": 73,
        "flagged": true,
        "reason": "The sanctioned amount is 1.7x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 34,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 20,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 38,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00056",
    "workName": "Construction of Crematorium Shed, Colony 15",
    "description": "Construction of Crematorium Shed, Colony 15 under MPLADS scheme, recommended by Richard Vanlalhmangaiha, MP for Mizoram (St).",
    "category": "Others",
    "state": "Mizoram",
    "constituency": "Mizoram (St)",
    "mpName": "Richard Vanlalhmangaiha",
    "authority": "Block Development Office, Mizoram (St)",
    "recommendationDate": "10 Jan 2021",
    "sanctionDate": "27 Oct 2023",
    "sanctionAmount": 29318000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 22282600,
    "lastExpenditureDate": "16 Nov 2026",
    "risk": {
      "overallScore": 57,
      "level": "MEDIUM",
      "cost": {
        "score": 75,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar others projects in the same district."
      },
      "delay": {
        "score": 33,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 35,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 90,
        "flagged": true,
        "reason": "A similar work description was found in Panchayat 12, Mizoram, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00057",
    "workName": "Improvement of Storm Water Drain, Sector 17",
    "description": "Improvement of Storm Water Drain, Sector 17 under MPLADS scheme, recommended by Richard Vanlalhmangaiha, MP for Mizoram (St).",
    "category": "Drainage",
    "state": "Mizoram",
    "constituency": "Mizoram (St)",
    "mpName": "Richard Vanlalhmangaiha",
    "authority": "Block Development Office, Mizoram (St)",
    "recommendationDate": "12 Sep 2022",
    "sanctionDate": "20 Apr 2022",
    "sanctionAmount": 21177000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Kisan Infra Developers",
    "totalDisbursed": 11778200,
    "lastExpenditureDate": "17 Jul 2026",
    "risk": {
      "overallScore": 79,
      "level": "HIGH",
      "cost": {
        "score": 94,
        "flagged": true,
        "reason": "The sanctioned amount is 1.7x higher than similar drainage projects in the same district."
      },
      "delay": {
        "score": 94,
        "flagged": true,
        "reason": "Project has remained in the 'Work in Progress' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 42,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 75,
        "flagged": true,
        "reason": "A similar work description was found in Panchayat 13, Mizoram, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00058",
    "workName": "Solid Waste Management Unit, Colony 17",
    "description": "Solid Waste Management Unit, Colony 17 under MPLADS scheme, recommended by Captain Brijesh Chowta, MP for Dakshina Kannada.",
    "category": "Sanitation",
    "state": "Karnataka",
    "constituency": "Dakshina Kannada",
    "mpName": "Captain Brijesh Chowta",
    "authority": "District Panchayat Dakshina Kannada",
    "recommendationDate": "21 Dec 2023",
    "sanctionDate": "16 Oct 2022",
    "sanctionAmount": 25061000,
    "workStage": "Work in Progress",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 10419400,
    "lastExpenditureDate": "26 Nov 2025",
    "risk": {
      "overallScore": 53,
      "level": "MEDIUM",
      "cost": {
        "score": 24,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 47,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 89,
        "flagged": true,
        "reason": "Expenditure of ₹10,419,400 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 70,
        "flagged": true,
        "reason": "A similar work description was found in Ward No. 19, Karnataka, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00059",
    "workName": "Widening of Approach Road, Sector 11",
    "description": "Widening of Approach Road, Sector 11 under MPLADS scheme, recommended by Captain Brijesh Chowta, MP for Dakshina Kannada.",
    "category": "Roads & Bridges",
    "state": "Karnataka",
    "constituency": "Dakshina Kannada",
    "mpName": "Captain Brijesh Chowta",
    "authority": "Block Development Office, Dakshina Kannada",
    "recommendationDate": "05 Dec 2021",
    "sanctionDate": "18 Apr 2024",
    "sanctionAmount": 9236000,
    "workStage": "Completed",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 9142000,
    "lastExpenditureDate": "16 Nov 2025",
    "risk": {
      "overallScore": 27,
      "level": "LOW",
      "cost": {
        "score": 21,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 44,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 26,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 14,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00060",
    "workName": "Upgradation of Primary Health Centre, Block 23",
    "description": "Upgradation of Primary Health Centre, Block 23 under MPLADS scheme, recommended by Rajkumar Chahar, MP for Fatehpur Sikri.",
    "category": "Health",
    "state": "Uttar Pradesh",
    "constituency": "Fatehpur Sikri",
    "mpName": "Rajkumar Chahar",
    "authority": "Block Development Office, Fatehpur Sikri",
    "recommendationDate": "18 Nov 2023",
    "sanctionDate": "27 Jul 2023",
    "sanctionAmount": 24599000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Kisan Infra Developers",
    "totalDisbursed": 22805000,
    "lastExpenditureDate": "10 Mar 2025",
    "risk": {
      "overallScore": 49,
      "level": "MEDIUM",
      "cost": {
        "score": 15,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 81,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 270 days without progress update."
      },
      "expenditure": {
        "score": 82,
        "flagged": true,
        "reason": "Expenditure of ₹22,805,000 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 19,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00061",
    "workName": "Drinking Water Supply Scheme, Panchayat 2",
    "description": "Drinking Water Supply Scheme, Panchayat 2 under MPLADS scheme, recommended by Rajkumar Chahar, MP for Fatehpur Sikri.",
    "category": "Water Supply",
    "state": "Uttar Pradesh",
    "constituency": "Fatehpur Sikri",
    "mpName": "Rajkumar Chahar",
    "authority": "Zila Parishad Fatehpur Sikri",
    "recommendationDate": "18 Jan 2021",
    "sanctionDate": "21 Jul 2022",
    "sanctionAmount": 24955000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 7363900,
    "lastExpenditureDate": "21 Aug 2025",
    "risk": {
      "overallScore": 19,
      "level": "LOW",
      "cost": {
        "score": 30,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 13,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 24,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 4,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00062",
    "workName": "Construction of Crematorium Shed, Panchayat 24",
    "description": "Construction of Crematorium Shed, Panchayat 24 under MPLADS scheme, recommended by Radhe Shyam Rathiya, MP for Raigarh(St).",
    "category": "Others",
    "state": "Chhattisgarh",
    "constituency": "Raigarh(St)",
    "mpName": "Radhe Shyam Rathiya",
    "authority": "District Rural Development Agency, Raigarh(St)",
    "recommendationDate": "16 Sep 2023",
    "sanctionDate": "15 Sep 2022",
    "sanctionAmount": 31789000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Om Construction Co.",
    "totalDisbursed": 2708200,
    "lastExpenditureDate": "26 Apr 2025",
    "risk": {
      "overallScore": 43,
      "level": "MEDIUM",
      "cost": {
        "score": 86,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar others projects in the same district."
      },
      "delay": {
        "score": 10,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 46,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 14,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00063",
    "workName": "Construction of Community Toilet Complex, Ward No. 13",
    "description": "Construction of Community Toilet Complex, Ward No. 13 under MPLADS scheme, recommended by Radhe Shyam Rathiya, MP for Raigarh(St).",
    "category": "Sanitation",
    "state": "Chhattisgarh",
    "constituency": "Raigarh(St)",
    "mpName": "Radhe Shyam Rathiya",
    "authority": "Zila Parishad Raigarh(St)",
    "recommendationDate": "19 May 2022",
    "sanctionDate": "01 Oct 2024",
    "sanctionAmount": 10414000,
    "workStage": "Work in Progress",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 3765900,
    "lastExpenditureDate": "12 Nov 2025",
    "risk": {
      "overallScore": 40,
      "level": "MEDIUM",
      "cost": {
        "score": 75,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar sanitation projects in the same district."
      },
      "delay": {
        "score": 20,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 29,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 20,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00064",
    "workName": "Renovation of Primary School Building, Sector 5",
    "description": "Renovation of Primary School Building, Sector 5 under MPLADS scheme, recommended by Radhe Shyam Rathiya, MP for Raigarh(St).",
    "category": "Education",
    "state": "Chhattisgarh",
    "constituency": "Raigarh(St)",
    "mpName": "Radhe Shyam Rathiya",
    "authority": "Zila Parishad Raigarh(St)",
    "recommendationDate": "22 Apr 2021",
    "sanctionDate": "17 Feb 2024",
    "sanctionAmount": 20812000,
    "workStage": "Completed",
    "vendorName": "M/s Kisan Infra Developers",
    "totalDisbursed": 20042000,
    "lastExpenditureDate": "23 Sep 2025",
    "risk": {
      "overallScore": 41,
      "level": "MEDIUM",
      "cost": {
        "score": 17,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 45,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 74,
        "flagged": true,
        "reason": "Expenditure of ₹20,042,000 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 35,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00065",
    "workName": "Construction of Drainage System, Colony 15",
    "description": "Construction of Drainage System, Colony 15 under MPLADS scheme, recommended by Mala Rajya Laxmi Shah, MP for Tehri Garhwal.",
    "category": "Drainage",
    "state": "Uttarakhand",
    "constituency": "Tehri Garhwal",
    "mpName": "Mala Rajya Laxmi Shah",
    "authority": "District Rural Development Agency, Tehri Garhwal",
    "recommendationDate": "27 May 2022",
    "sanctionDate": "07 Dec 2022",
    "sanctionAmount": 18681000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Ganga Infrastructure Pvt. Ltd.",
    "totalDisbursed": 14231800,
    "lastExpenditureDate": "02 Feb 2026",
    "risk": {
      "overallScore": 41,
      "level": "MEDIUM",
      "cost": {
        "score": 44,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 14,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 91,
        "flagged": true,
        "reason": "Expenditure of ₹14,231,800 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 10,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00066",
    "workName": "Renovation of Panchayat Bhawan, Sector 13",
    "description": "Renovation of Panchayat Bhawan, Sector 13 under MPLADS scheme, recommended by Mala Rajya Laxmi Shah, MP for Tehri Garhwal.",
    "category": "Community Infrastructure",
    "state": "Uttarakhand",
    "constituency": "Tehri Garhwal",
    "mpName": "Mala Rajya Laxmi Shah",
    "authority": "District Rural Development Agency, Tehri Garhwal",
    "recommendationDate": "05 Sep 2022",
    "sanctionDate": "27 Apr 2024",
    "sanctionAmount": 8167000,
    "workStage": "Delayed",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 4471400,
    "lastExpenditureDate": "10 Jan 2024",
    "risk": {
      "overallScore": 26,
      "level": "LOW",
      "cost": {
        "score": 37,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 25,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 27,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 9,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00067",
    "workName": "Construction of CC Road at Panchayat 7",
    "description": "Construction of CC Road at Panchayat 7 under MPLADS scheme, recommended by Mala Rajya Laxmi Shah, MP for Tehri Garhwal.",
    "category": "Roads & Bridges",
    "state": "Uttarakhand",
    "constituency": "Tehri Garhwal",
    "mpName": "Mala Rajya Laxmi Shah",
    "authority": "Municipal Corporation Tehri Garhwal",
    "recommendationDate": "07 Sep 2021",
    "sanctionDate": "17 Mar 2022",
    "sanctionAmount": 8069000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 723500,
    "lastExpenditureDate": "27 Apr 2025",
    "risk": {
      "overallScore": 33,
      "level": "LOW",
      "cost": {
        "score": 46,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 30,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 19,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 35,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00068",
    "workName": "Renovation of Primary School Building, Gram 22",
    "description": "Renovation of Primary School Building, Gram 22 under MPLADS scheme, recommended by Appalanaidu Kalisetti, MP for Vizianagaram.",
    "category": "Education",
    "state": "Andhra Pradesh",
    "constituency": "Vizianagaram",
    "mpName": "Appalanaidu Kalisetti",
    "authority": "Municipal Corporation Vizianagaram",
    "recommendationDate": "10 Mar 2022",
    "sanctionDate": "25 Mar 2023",
    "sanctionAmount": 21241000,
    "workStage": "Sanctioned",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 1097400,
    "lastExpenditureDate": "08 Aug 2026",
    "risk": {
      "overallScore": 20,
      "level": "LOW",
      "cost": {
        "score": 19,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 13,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 36,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 10,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00069",
    "workName": "Construction of Drainage System, Sector 12",
    "description": "Construction of Drainage System, Sector 12 under MPLADS scheme, recommended by Shyamkumar, MP for Ramtek(Sc).",
    "category": "Drainage",
    "state": "Maharashtra",
    "constituency": "Ramtek(Sc)",
    "mpName": "Shyamkumar",
    "authority": "Municipal Corporation Ramtek(Sc)",
    "recommendationDate": "22 Dec 2023",
    "sanctionDate": "16 Apr 2024",
    "sanctionAmount": 20736000,
    "workStage": "Completed",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 19142700,
    "lastExpenditureDate": "10 Jun 2024",
    "risk": {
      "overallScore": 45,
      "level": "MEDIUM",
      "cost": {
        "score": 78,
        "flagged": true,
        "reason": "The sanctioned amount is 2.3x higher than similar drainage projects in the same district."
      },
      "delay": {
        "score": 17,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 48,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 27,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00070",
    "workName": "Construction of Sub-Health Centre, Sector 15",
    "description": "Construction of Sub-Health Centre, Sector 15 under MPLADS scheme, recommended by Shyamkumar, MP for Ramtek(Sc).",
    "category": "Health",
    "state": "Maharashtra",
    "constituency": "Ramtek(Sc)",
    "mpName": "Shyamkumar",
    "authority": "Municipal Corporation Ramtek(Sc)",
    "recommendationDate": "12 Apr 2022",
    "sanctionDate": "02 Jul 2023",
    "sanctionAmount": 12933000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 5945300,
    "lastExpenditureDate": "24 Apr 2026",
    "risk": {
      "overallScore": 72,
      "level": "HIGH",
      "cost": {
        "score": 90,
        "flagged": true,
        "reason": "The sanctioned amount is 1.9x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 74,
        "flagged": true,
        "reason": "Project has remained in the 'Work in Progress' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 89,
        "flagged": true,
        "reason": "Expenditure of ₹5,945,300 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 17,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00071",
    "workName": "Village Street Light Improvement, Sector 6",
    "description": "Village Street Light Improvement, Sector 6 under MPLADS scheme, recommended by Dharmendra Pradhan, MP for Sambalpur.",
    "category": "Others",
    "state": "Odisha",
    "constituency": "Sambalpur",
    "mpName": "Dharmendra Pradhan",
    "authority": "District Panchayat Sambalpur",
    "recommendationDate": "02 Sep 2021",
    "sanctionDate": "02 Nov 2022",
    "sanctionAmount": 27216000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 12784500,
    "lastExpenditureDate": "05 Jul 2024",
    "risk": {
      "overallScore": 45,
      "level": "MEDIUM",
      "cost": {
        "score": 94,
        "flagged": true,
        "reason": "The sanctioned amount is 1.5x higher than similar others projects in the same district."
      },
      "delay": {
        "score": 23,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 13,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 32,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00072",
    "workName": "Construction of Village Haat/Market Shed, Ward No. 1",
    "description": "Construction of Village Haat/Market Shed, Ward No. 1 under MPLADS scheme, recommended by Dharmendra Pradhan, MP for Sambalpur.",
    "category": "Community Infrastructure",
    "state": "Odisha",
    "constituency": "Sambalpur",
    "mpName": "Dharmendra Pradhan",
    "authority": "District Panchayat Sambalpur",
    "recommendationDate": "04 Feb 2021",
    "sanctionDate": "08 Mar 2024",
    "sanctionAmount": 20695000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 17471800,
    "lastExpenditureDate": "17 Oct 2024",
    "risk": {
      "overallScore": 41,
      "level": "MEDIUM",
      "cost": {
        "score": 35,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 39,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 79,
        "flagged": true,
        "reason": "Expenditure of ₹17,471,800 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 7,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00073",
    "workName": "Construction of Village Haat/Market Shed, Sector 13",
    "description": "Construction of Village Haat/Market Shed, Sector 13 under MPLADS scheme, recommended by Dharmendra Pradhan, MP for Sambalpur.",
    "category": "Community Infrastructure",
    "state": "Odisha",
    "constituency": "Sambalpur",
    "mpName": "Dharmendra Pradhan",
    "authority": "District Rural Development Agency, Sambalpur",
    "recommendationDate": "02 Sep 2021",
    "sanctionDate": "28 Apr 2022",
    "sanctionAmount": 12973000,
    "workStage": "Completed",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 12604500,
    "lastExpenditureDate": "16 Oct 2026",
    "risk": {
      "overallScore": 53,
      "level": "MEDIUM",
      "cost": {
        "score": 27,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 46,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 85,
        "flagged": true,
        "reason": "Expenditure of ₹12,604,500 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 68,
        "flagged": true,
        "reason": "A similar work description was found in Colony 5, Odisha, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00074",
    "workName": "Construction of School Boundary Wall, Colony 8",
    "description": "Construction of School Boundary Wall, Colony 8 under MPLADS scheme, recommended by Ravindra Shyamnarayan Alias Ravi Kishan Shukla, MP for Gorakhpur.",
    "category": "Education",
    "state": "Uttar Pradesh",
    "constituency": "Gorakhpur",
    "mpName": "Ravindra Shyamnarayan Alias Ravi Kishan Shukla",
    "authority": "District Rural Development Agency, Gorakhpur",
    "recommendationDate": "17 Feb 2023",
    "sanctionDate": "02 Jun 2024",
    "sanctionAmount": 28208000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 24384800,
    "lastExpenditureDate": "08 Jul 2024",
    "risk": {
      "overallScore": 52,
      "level": "MEDIUM",
      "cost": {
        "score": 49,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 85,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 185 days without progress update."
      },
      "expenditure": {
        "score": 38,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 24,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00075",
    "workName": "Renovation of Panchayat Bhawan, Ward No. 20",
    "description": "Renovation of Panchayat Bhawan, Ward No. 20 under MPLADS scheme, recommended by Ravindra Shyamnarayan Alias Ravi Kishan Shukla, MP for Gorakhpur.",
    "category": "Community Infrastructure",
    "state": "Uttar Pradesh",
    "constituency": "Gorakhpur",
    "mpName": "Ravindra Shyamnarayan Alias Ravi Kishan Shukla",
    "authority": "Block Development Office, Gorakhpur",
    "recommendationDate": "04 Jun 2022",
    "sanctionDate": "10 Jan 2022",
    "sanctionAmount": 22056000,
    "workStage": "Completed",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 21410000,
    "lastExpenditureDate": "25 Jun 2025",
    "risk": {
      "overallScore": 54,
      "level": "MEDIUM",
      "cost": {
        "score": 77,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 45,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 16,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 77,
        "flagged": true,
        "reason": "A similar work description was found in Colony 3, Uttar Pradesh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00076",
    "workName": "Renovation of Panchayat Bhawan, Ward No. 10",
    "description": "Renovation of Panchayat Bhawan, Ward No. 10 under MPLADS scheme, recommended by Bharatsinhji Shankarji Dabhi, MP for Patan.",
    "category": "Community Infrastructure",
    "state": "Gujarat",
    "constituency": "Patan",
    "mpName": "Bharatsinhji Shankarji Dabhi",
    "authority": "Zila Parishad Patan",
    "recommendationDate": "05 Mar 2022",
    "sanctionDate": "09 May 2023",
    "sanctionAmount": 17041000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 2303400,
    "lastExpenditureDate": "03 Mar 2025",
    "risk": {
      "overallScore": 60,
      "level": "MEDIUM",
      "cost": {
        "score": 81,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 81,
        "flagged": true,
        "reason": "Project has remained in the 'Sanctioned' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 41,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 14,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00077",
    "workName": "Widening of Approach Road, Sector 11",
    "description": "Widening of Approach Road, Sector 11 under MPLADS scheme, recommended by Bharatsinhji Shankarji Dabhi, MP for Patan.",
    "category": "Roads & Bridges",
    "state": "Gujarat",
    "constituency": "Patan",
    "mpName": "Bharatsinhji Shankarji Dabhi",
    "authority": "Block Development Office, Patan",
    "recommendationDate": "23 Oct 2022",
    "sanctionDate": "11 Aug 2022",
    "sanctionAmount": 24262000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 14968800,
    "lastExpenditureDate": "11 Jul 2024",
    "risk": {
      "overallScore": 35,
      "level": "LOW",
      "cost": {
        "score": 41,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 25,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 35,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 38,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00078",
    "workName": "Construction of Crematorium Shed, Gram 7",
    "description": "Construction of Crematorium Shed, Gram 7 under MPLADS scheme, recommended by Murlidhar Mohol, MP for Pune.",
    "category": "Others",
    "state": "Maharashtra",
    "constituency": "Pune",
    "mpName": "Murlidhar Mohol",
    "authority": "District Panchayat Pune",
    "recommendationDate": "09 Apr 2022",
    "sanctionDate": "23 Mar 2024",
    "sanctionAmount": 27284000,
    "workStage": "Completed",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 26570200,
    "lastExpenditureDate": "03 Jul 2025",
    "risk": {
      "overallScore": 40,
      "level": "MEDIUM",
      "cost": {
        "score": 47,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 42,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 33,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 36,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00079",
    "workName": "Construction of Community Toilet Complex, Panchayat 21",
    "description": "Construction of Community Toilet Complex, Panchayat 21 under MPLADS scheme, recommended by Raju Bista, MP for Darjeeling.",
    "category": "Sanitation",
    "state": "West Bengal",
    "constituency": "Darjeeling",
    "mpName": "Raju Bista",
    "authority": "District Panchayat Darjeeling",
    "recommendationDate": "08 May 2021",
    "sanctionDate": "17 Dec 2024",
    "sanctionAmount": 21425000,
    "workStage": "Completed",
    "vendorName": "M/s Kisan Infra Developers",
    "totalDisbursed": 21075700,
    "lastExpenditureDate": "23 Oct 2026",
    "risk": {
      "overallScore": 43,
      "level": "MEDIUM",
      "cost": {
        "score": 35,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 47,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 66,
        "flagged": true,
        "reason": "Expenditure of ₹21,075,700 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 20,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00080",
    "workName": "Renovation of Primary School Building, Block 10",
    "description": "Renovation of Primary School Building, Block 10 under MPLADS scheme, recommended by Raju Bista, MP for Darjeeling.",
    "category": "Education",
    "state": "West Bengal",
    "constituency": "Darjeeling",
    "mpName": "Raju Bista",
    "authority": "Zila Parishad Darjeeling",
    "recommendationDate": "26 Jan 2022",
    "sanctionDate": "01 Feb 2024",
    "sanctionAmount": 15999000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 7427900,
    "lastExpenditureDate": "04 Nov 2025",
    "risk": {
      "overallScore": 60,
      "level": "MEDIUM",
      "cost": {
        "score": 95,
        "flagged": true,
        "reason": "The sanctioned amount is 1.6x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 21,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 92,
        "flagged": true,
        "reason": "Expenditure of ₹7,427,900 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 16,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00081",
    "workName": "Construction of Village Haat/Market Shed, Ward No. 24",
    "description": "Construction of Village Haat/Market Shed, Ward No. 24 under MPLADS scheme, recommended by Isha Khan Choudhury, MP for Maldaha Dakshin.",
    "category": "Community Infrastructure",
    "state": "West Bengal",
    "constituency": "Maldaha Dakshin",
    "mpName": "Isha Khan Choudhury",
    "authority": "Municipal Corporation Maldaha Dakshin",
    "recommendationDate": "04 Oct 2021",
    "sanctionDate": "12 Mar 2024",
    "sanctionAmount": 29419000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 19863100,
    "lastExpenditureDate": "15 Apr 2025",
    "risk": {
      "overallScore": 74,
      "level": "HIGH",
      "cost": {
        "score": 87,
        "flagged": true,
        "reason": "The sanctioned amount is 1.9x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 90,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 310 days without progress update."
      },
      "expenditure": {
        "score": 87,
        "flagged": true,
        "reason": "Expenditure of ₹19,863,100 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 13,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00082",
    "workName": "Improvement of Storm Water Drain, Gram 5",
    "description": "Improvement of Storm Water Drain, Gram 5 under MPLADS scheme, recommended by Isha Khan Choudhury, MP for Maldaha Dakshin.",
    "category": "Drainage",
    "state": "West Bengal",
    "constituency": "Maldaha Dakshin",
    "mpName": "Isha Khan Choudhury",
    "authority": "District Rural Development Agency, Maldaha Dakshin",
    "recommendationDate": "06 Jul 2022",
    "sanctionDate": "18 Nov 2023",
    "sanctionAmount": 8235000,
    "workStage": "Work in Progress",
    "vendorName": "M/s United Builders & Co.",
    "totalDisbursed": 4628500,
    "lastExpenditureDate": "06 Nov 2026",
    "risk": {
      "overallScore": 42,
      "level": "MEDIUM",
      "cost": {
        "score": 18,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 38,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 87,
        "flagged": true,
        "reason": "Expenditure of ₹4,628,500 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 33,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00083",
    "workName": "Construction of Crematorium Shed, Sector 22",
    "description": "Construction of Crematorium Shed, Sector 22 under MPLADS scheme, recommended by Isha Khan Choudhury, MP for Maldaha Dakshin.",
    "category": "Others",
    "state": "West Bengal",
    "constituency": "Maldaha Dakshin",
    "mpName": "Isha Khan Choudhury",
    "authority": "Block Development Office, Maldaha Dakshin",
    "recommendationDate": "18 Apr 2022",
    "sanctionDate": "25 Mar 2023",
    "sanctionAmount": 13193000,
    "workStage": "Completed",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 12940800,
    "lastExpenditureDate": "24 Oct 2025",
    "risk": {
      "overallScore": 26,
      "level": "LOW",
      "cost": {
        "score": 42,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 17,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 33,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 4,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00084",
    "workName": "Construction of Drainage System, Gram 21",
    "description": "Construction of Drainage System, Gram 21 under MPLADS scheme, recommended by Balya Mama Suresh Gopinath Mhatre, MP for Bhiwandi.",
    "category": "Drainage",
    "state": "Maharashtra",
    "constituency": "Bhiwandi",
    "mpName": "Balya Mama Suresh Gopinath Mhatre",
    "authority": "Municipal Corporation Bhiwandi",
    "recommendationDate": "26 Apr 2021",
    "sanctionDate": "23 Oct 2024",
    "sanctionAmount": 14790000,
    "workStage": "Delayed",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 8103200,
    "lastExpenditureDate": "20 Dec 2025",
    "risk": {
      "overallScore": 36,
      "level": "LOW",
      "cost": {
        "score": 76,
        "flagged": true,
        "reason": "The sanctioned amount is 2.1x higher than similar drainage projects in the same district."
      },
      "delay": {
        "score": 13,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 27,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 12,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00085",
    "workName": "Upgradation of Primary Health Centre, Colony 22",
    "description": "Upgradation of Primary Health Centre, Colony 22 under MPLADS scheme, recommended by Balya Mama Suresh Gopinath Mhatre, MP for Bhiwandi.",
    "category": "Health",
    "state": "Maharashtra",
    "constituency": "Bhiwandi",
    "mpName": "Balya Mama Suresh Gopinath Mhatre",
    "authority": "District Rural Development Agency, Bhiwandi",
    "recommendationDate": "05 Apr 2021",
    "sanctionDate": "27 Jun 2024",
    "sanctionAmount": 9658000,
    "workStage": "Completed",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 9392100,
    "lastExpenditureDate": "13 Nov 2024",
    "risk": {
      "overallScore": 37,
      "level": "LOW",
      "cost": {
        "score": 27,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 34,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 70,
        "flagged": true,
        "reason": "Expenditure of ₹9,392,100 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 19,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00086",
    "workName": "Construction of Community Toilet Complex, Colony 1",
    "description": "Construction of Community Toilet Complex, Colony 1 under MPLADS scheme, recommended by Balya Mama Suresh Gopinath Mhatre, MP for Bhiwandi.",
    "category": "Sanitation",
    "state": "Maharashtra",
    "constituency": "Bhiwandi",
    "mpName": "Balya Mama Suresh Gopinath Mhatre",
    "authority": "District Panchayat Bhiwandi",
    "recommendationDate": "16 Apr 2022",
    "sanctionDate": "27 Jun 2023",
    "sanctionAmount": 21356000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Om Construction Co.",
    "totalDisbursed": 13287000,
    "lastExpenditureDate": "18 Jun 2025",
    "risk": {
      "overallScore": 50,
      "level": "MEDIUM",
      "cost": {
        "score": 41,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 13,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 94,
        "flagged": true,
        "reason": "Expenditure of ₹13,287,000 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 65,
        "flagged": true,
        "reason": "A similar work description was found in Sector 15, Maharashtra, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00087",
    "workName": "Construction of Additional Classroom, Govt School Gram 10",
    "description": "Construction of Additional Classroom, Govt School Gram 10 under MPLADS scheme, recommended by Arun Govil, MP for Meerut.",
    "category": "Education",
    "state": "Uttar Pradesh",
    "constituency": "Meerut",
    "mpName": "Arun Govil",
    "authority": "Zila Parishad Meerut",
    "recommendationDate": "21 Jul 2021",
    "sanctionDate": "23 Dec 2023",
    "sanctionAmount": 29202000,
    "workStage": "Completed",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 28418200,
    "lastExpenditureDate": "21 Jul 2024",
    "risk": {
      "overallScore": 62,
      "level": "MEDIUM",
      "cost": {
        "score": 78,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 79,
        "flagged": true,
        "reason": "Project has remained in the 'Completed' stage for more than 310 days without progress update."
      },
      "expenditure": {
        "score": 10,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 76,
        "flagged": true,
        "reason": "A similar work description was found in Ward No. 14, Uttar Pradesh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00088",
    "workName": "Construction of Drainage System, Panchayat 13",
    "description": "Construction of Drainage System, Panchayat 13 under MPLADS scheme, recommended by Arun Govil, MP for Meerut.",
    "category": "Drainage",
    "state": "Uttar Pradesh",
    "constituency": "Meerut",
    "mpName": "Arun Govil",
    "authority": "District Panchayat Meerut",
    "recommendationDate": "22 Nov 2021",
    "sanctionDate": "17 Feb 2022",
    "sanctionAmount": 20524000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 13267600,
    "lastExpenditureDate": "20 Jan 2026",
    "risk": {
      "overallScore": 22,
      "level": "LOW",
      "cost": {
        "score": 23,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 19,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 38,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 7,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00089",
    "workName": "Construction of Community Toilet Complex, Sector 11",
    "description": "Construction of Community Toilet Complex, Sector 11 under MPLADS scheme, recommended by Kangana Ranaut, MP for Mandi.",
    "category": "Sanitation",
    "state": "Himachal Pradesh",
    "constituency": "Mandi",
    "mpName": "Kangana Ranaut",
    "authority": "Zila Parishad Mandi",
    "recommendationDate": "10 Nov 2021",
    "sanctionDate": "20 Sep 2022",
    "sanctionAmount": 13542000,
    "workStage": "Completed",
    "vendorName": "M/s Om Construction Co.",
    "totalDisbursed": 12767300,
    "lastExpenditureDate": "24 Apr 2026",
    "risk": {
      "overallScore": 34,
      "level": "LOW",
      "cost": {
        "score": 25,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 17,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 48,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 55,
        "flagged": true,
        "reason": "A similar work description was found in Block 11, Himachal Pradesh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00090",
    "workName": "Construction of Village Haat/Market Shed, Block 18",
    "description": "Construction of Village Haat/Market Shed, Block 18 under MPLADS scheme, recommended by Kangana Ranaut, MP for Mandi.",
    "category": "Community Infrastructure",
    "state": "Himachal Pradesh",
    "constituency": "Mandi",
    "mpName": "Kangana Ranaut",
    "authority": "District Rural Development Agency, Mandi",
    "recommendationDate": "17 Jul 2021",
    "sanctionDate": "23 Nov 2023",
    "sanctionAmount": 10593000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 8533500,
    "lastExpenditureDate": "14 Jul 2026",
    "risk": {
      "overallScore": 67,
      "level": "MEDIUM",
      "cost": {
        "score": 89,
        "flagged": true,
        "reason": "The sanctioned amount is 1.9x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 70,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 240 days without progress update."
      },
      "expenditure": {
        "score": 78,
        "flagged": true,
        "reason": "Expenditure of ₹8,533,500 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 11,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00091",
    "workName": "Improvement of Storm Water Drain, Block 23",
    "description": "Improvement of Storm Water Drain, Block 23 under MPLADS scheme, recommended by Kangana Ranaut, MP for Mandi.",
    "category": "Drainage",
    "state": "Himachal Pradesh",
    "constituency": "Mandi",
    "mpName": "Kangana Ranaut",
    "authority": "District Rural Development Agency, Mandi",
    "recommendationDate": "24 Nov 2022",
    "sanctionDate": "06 Dec 2024",
    "sanctionAmount": 21390000,
    "workStage": "Completed",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 20454600,
    "lastExpenditureDate": "23 Jan 2024",
    "risk": {
      "overallScore": 70,
      "level": "HIGH",
      "cost": {
        "score": 87,
        "flagged": true,
        "reason": "The sanctioned amount is 2.3x higher than similar drainage projects in the same district."
      },
      "delay": {
        "score": 81,
        "flagged": true,
        "reason": "Project has remained in the 'Completed' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 82,
        "flagged": true,
        "reason": "Expenditure of ₹20,454,600 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 9,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00092",
    "workName": "Upgradation of Primary Health Centre, Gram 19",
    "description": "Upgradation of Primary Health Centre, Gram 19 under MPLADS scheme, recommended by Mukesh Rajput, MP for Farrukhabad.",
    "category": "Health",
    "state": "Uttar Pradesh",
    "constituency": "Farrukhabad",
    "mpName": "Mukesh Rajput",
    "authority": "Zila Parishad Farrukhabad",
    "recommendationDate": "24 Nov 2023",
    "sanctionDate": "24 Apr 2022",
    "sanctionAmount": 19749000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Om Construction Co.",
    "totalDisbursed": 13002900,
    "lastExpenditureDate": "02 Jan 2026",
    "risk": {
      "overallScore": 51,
      "level": "MEDIUM",
      "cost": {
        "score": 73,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 74,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 12,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 28,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00093",
    "workName": "Construction of Sub-Health Centre, Ward No. 19",
    "description": "Construction of Sub-Health Centre, Ward No. 19 under MPLADS scheme, recommended by Bharti Pardhi, MP for Balaghat.",
    "category": "Health",
    "state": "Madhya Pradesh",
    "constituency": "Balaghat",
    "mpName": "Bharti Pardhi",
    "authority": "Zila Parishad Balaghat",
    "recommendationDate": "25 May 2022",
    "sanctionDate": "03 Jun 2023",
    "sanctionAmount": 10854000,
    "workStage": "Completed",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 10025600,
    "lastExpenditureDate": "01 Aug 2026",
    "risk": {
      "overallScore": 58,
      "level": "MEDIUM",
      "cost": {
        "score": 97,
        "flagged": true,
        "reason": "The sanctioned amount is 1.7x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 49,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 47,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 14,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00094",
    "workName": "Repair of Village Road near Sector 1",
    "description": "Repair of Village Road near Sector 1 under MPLADS scheme, recommended by Bharti Pardhi, MP for Balaghat.",
    "category": "Roads & Bridges",
    "state": "Madhya Pradesh",
    "constituency": "Balaghat",
    "mpName": "Bharti Pardhi",
    "authority": "District Panchayat Balaghat",
    "recommendationDate": "10 Dec 2023",
    "sanctionDate": "17 Apr 2022",
    "sanctionAmount": 20392000,
    "workStage": "Completed",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 19998700,
    "lastExpenditureDate": "16 Jul 2024",
    "risk": {
      "overallScore": 25,
      "level": "LOW",
      "cost": {
        "score": 19,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 15,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 43,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 25,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00095",
    "workName": "Construction of Additional Classroom, Govt School Gram 13",
    "description": "Construction of Additional Classroom, Govt School Gram 13 under MPLADS scheme, recommended by Chandra Prakash Joshi, MP for Chittorgarh.",
    "category": "Education",
    "state": "Rajasthan",
    "constituency": "Chittorgarh",
    "mpName": "Chandra Prakash Joshi",
    "authority": "District Rural Development Agency, Chittorgarh",
    "recommendationDate": "27 Dec 2022",
    "sanctionDate": "11 Jun 2024",
    "sanctionAmount": 22141000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 2200100,
    "lastExpenditureDate": "08 May 2025",
    "risk": {
      "overallScore": 76,
      "level": "HIGH",
      "cost": {
        "score": 96,
        "flagged": true,
        "reason": "The sanctioned amount is 2.1x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 71,
        "flagged": true,
        "reason": "Project has remained in the 'Sanctioned' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 85,
        "flagged": true,
        "reason": "Expenditure of ₹2,200,100 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 36,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00096",
    "workName": "Upgradation of Primary Health Centre, Ward No. 3",
    "description": "Upgradation of Primary Health Centre, Ward No. 3 under MPLADS scheme, recommended by Shri Tapir Gao, MP for Arunachal East.",
    "category": "Health",
    "state": "Arunachal Pradesh",
    "constituency": "Arunachal East",
    "mpName": "Shri Tapir Gao",
    "authority": "District Panchayat Arunachal East",
    "recommendationDate": "12 Apr 2023",
    "sanctionDate": "02 Sep 2023",
    "sanctionAmount": 27532000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 14357600,
    "lastExpenditureDate": "09 May 2026",
    "risk": {
      "overallScore": 72,
      "level": "HIGH",
      "cost": {
        "score": 84,
        "flagged": true,
        "reason": "The sanctioned amount is 2.2x higher than similar health projects in the same district."
      },
      "delay": {
        "score": 45,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 94,
        "flagged": true,
        "reason": "Expenditure of ₹14,357,600 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 63,
        "flagged": true,
        "reason": "A similar work description was found in Ward No. 1, Arunachal Pradesh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00097",
    "workName": "Installation of Bore Well and Hand Pump, Panchayat 7",
    "description": "Installation of Bore Well and Hand Pump, Panchayat 7 under MPLADS scheme, recommended by Shri Tapir Gao, MP for Arunachal East.",
    "category": "Water Supply",
    "state": "Arunachal Pradesh",
    "constituency": "Arunachal East",
    "mpName": "Shri Tapir Gao",
    "authority": "Municipal Corporation Arunachal East",
    "recommendationDate": "21 Apr 2021",
    "sanctionDate": "03 Mar 2023",
    "sanctionAmount": 13533000,
    "workStage": "Completed",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 13330300,
    "lastExpenditureDate": "02 Feb 2025",
    "risk": {
      "overallScore": 62,
      "level": "MEDIUM",
      "cost": {
        "score": 90,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar water supply projects in the same district."
      },
      "delay": {
        "score": 35,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 92,
        "flagged": true,
        "reason": "Expenditure of ₹13,330,300 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 15,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00098",
    "workName": "Construction of School Boundary Wall, Ward No. 20",
    "description": "Construction of School Boundary Wall, Ward No. 20 under MPLADS scheme, recommended by Shri Tapir Gao, MP for Arunachal East.",
    "category": "Education",
    "state": "Arunachal Pradesh",
    "constituency": "Arunachal East",
    "mpName": "Shri Tapir Gao",
    "authority": "Zila Parishad Arunachal East",
    "recommendationDate": "21 Apr 2022",
    "sanctionDate": "21 Apr 2024",
    "sanctionAmount": 16408000,
    "workStage": "Completed",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 15210500,
    "lastExpenditureDate": "13 Jan 2026",
    "risk": {
      "overallScore": 31,
      "level": "LOW",
      "cost": {
        "score": 44,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 32,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 34,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 3,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00099",
    "workName": "Construction of Culvert at Sector 17",
    "description": "Construction of Culvert at Sector 17 under MPLADS scheme, recommended by Ram Prasad Chaudhary, MP for Basti.",
    "category": "Roads & Bridges",
    "state": "Uttar Pradesh",
    "constituency": "Basti",
    "mpName": "Ram Prasad Chaudhary",
    "authority": "Zila Parishad Basti",
    "recommendationDate": "25 Jan 2023",
    "sanctionDate": "28 Oct 2022",
    "sanctionAmount": 36826000,
    "workStage": "Delayed",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 17886400,
    "lastExpenditureDate": "27 Jun 2025",
    "risk": {
      "overallScore": 61,
      "level": "MEDIUM",
      "cost": {
        "score": 79,
        "flagged": true,
        "reason": "The sanctioned amount is 1.9x higher than similar roads & bridges projects in the same district."
      },
      "delay": {
        "score": 32,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 87,
        "flagged": true,
        "reason": "Expenditure of ₹17,886,400 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 38,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00100",
    "workName": "Installation of Solar Street Lights, Colony 10",
    "description": "Installation of Solar Street Lights, Colony 10 under MPLADS scheme, recommended by Ram Prasad Chaudhary, MP for Basti.",
    "category": "Others",
    "state": "Uttar Pradesh",
    "constituency": "Basti",
    "mpName": "Ram Prasad Chaudhary",
    "authority": "Zila Parishad Basti",
    "recommendationDate": "11 Mar 2021",
    "sanctionDate": "26 Mar 2024",
    "sanctionAmount": 22320000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 778800,
    "lastExpenditureDate": "01 Jan 2025",
    "risk": {
      "overallScore": 58,
      "level": "MEDIUM",
      "cost": {
        "score": 76,
        "flagged": true,
        "reason": "The sanctioned amount is 2.1x higher than similar others projects in the same district."
      },
      "delay": {
        "score": 33,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 90,
        "flagged": true,
        "reason": "Expenditure of ₹778,800 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 23,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00101",
    "workName": "Installation of Solar Street Lights, Gram 11",
    "description": "Installation of Solar Street Lights, Gram 11 under MPLADS scheme, recommended by Eatala Rajender, MP for Malkajgiri.",
    "category": "Others",
    "state": "Telangana",
    "constituency": "Malkajgiri",
    "mpName": "Eatala Rajender",
    "authority": "District Panchayat Malkajgiri",
    "recommendationDate": "24 May 2022",
    "sanctionDate": "05 May 2024",
    "sanctionAmount": 55744000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 40408200,
    "lastExpenditureDate": "01 Dec 2024",
    "risk": {
      "overallScore": 46,
      "level": "MEDIUM",
      "cost": {
        "score": 35,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 46,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 85,
        "flagged": true,
        "reason": "Expenditure of ₹40,408,200 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 16,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00102",
    "workName": "Construction of Additional Classroom, Govt School Block 24",
    "description": "Construction of Additional Classroom, Govt School Block 24 under MPLADS scheme, recommended by Eatala Rajender, MP for Malkajgiri.",
    "category": "Education",
    "state": "Telangana",
    "constituency": "Malkajgiri",
    "mpName": "Eatala Rajender",
    "authority": "District Panchayat Malkajgiri",
    "recommendationDate": "01 Aug 2022",
    "sanctionDate": "08 Apr 2023",
    "sanctionAmount": 24581000,
    "workStage": "Delayed",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 10414600,
    "lastExpenditureDate": "12 Feb 2026",
    "risk": {
      "overallScore": 61,
      "level": "MEDIUM",
      "cost": {
        "score": 72,
        "flagged": true,
        "reason": "The sanctioned amount is 1.4x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 91,
        "flagged": true,
        "reason": "Project has remained in the 'Delayed' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 41,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 24,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00103",
    "workName": "Construction of Overhead Water Tank, Panchayat 15",
    "description": "Construction of Overhead Water Tank, Panchayat 15 under MPLADS scheme, recommended by Eatala Rajender, MP for Malkajgiri.",
    "category": "Water Supply",
    "state": "Telangana",
    "constituency": "Malkajgiri",
    "mpName": "Eatala Rajender",
    "authority": "Block Development Office, Malkajgiri",
    "recommendationDate": "03 Dec 2021",
    "sanctionDate": "11 Feb 2024",
    "sanctionAmount": 45937000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Kisan Infra Developers",
    "totalDisbursed": 138300,
    "lastExpenditureDate": "16 Oct 2026",
    "risk": {
      "overallScore": 39,
      "level": "LOW",
      "cost": {
        "score": 20,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 37,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 86,
        "flagged": true,
        "reason": "Expenditure of ₹138,300 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 14,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00104",
    "workName": "Upgradation of Primary Health Centre, Block 8",
    "description": "Upgradation of Primary Health Centre, Block 8 under MPLADS scheme, recommended by Ramesh Chandappa Jigajinagi, MP for Bijapur(Sc).",
    "category": "Health",
    "state": "Karnataka",
    "constituency": "Bijapur(Sc)",
    "mpName": "Ramesh Chandappa Jigajinagi",
    "authority": "Municipal Corporation Bijapur(Sc)",
    "recommendationDate": "20 Nov 2023",
    "sanctionDate": "04 Apr 2023",
    "sanctionAmount": 15749000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Om Construction Co.",
    "totalDisbursed": 11438300,
    "lastExpenditureDate": "06 Apr 2024",
    "risk": {
      "overallScore": 59,
      "level": "MEDIUM",
      "cost": {
        "score": 40,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 90,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 270 days without progress update."
      },
      "expenditure": {
        "score": 26,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 89,
        "flagged": true,
        "reason": "A similar work description was found in Sector 6, Karnataka, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00105",
    "workName": "Construction of Community Toilet Complex, Panchayat 15",
    "description": "Construction of Community Toilet Complex, Panchayat 15 under MPLADS scheme, recommended by Ramesh Chandappa Jigajinagi, MP for Bijapur(Sc).",
    "category": "Sanitation",
    "state": "Karnataka",
    "constituency": "Bijapur(Sc)",
    "mpName": "Ramesh Chandappa Jigajinagi",
    "authority": "Block Development Office, Bijapur(Sc)",
    "recommendationDate": "12 Nov 2021",
    "sanctionDate": "25 Jul 2024",
    "sanctionAmount": 24046000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 14946400,
    "lastExpenditureDate": "18 Apr 2026",
    "risk": {
      "overallScore": 77,
      "level": "HIGH",
      "cost": {
        "score": 88,
        "flagged": true,
        "reason": "The sanctioned amount is 1.8x higher than similar sanitation projects in the same district."
      },
      "delay": {
        "score": 95,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 310 days without progress update."
      },
      "expenditure": {
        "score": 40,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 80,
        "flagged": true,
        "reason": "A similar work description was found in Gram 2, Karnataka, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00106",
    "workName": "Construction of Drainage System, Sector 6",
    "description": "Construction of Drainage System, Sector 6 under MPLADS scheme, recommended by Rajesh Verma, MP for Khagaria.",
    "category": "Drainage",
    "state": "Bihar",
    "constituency": "Khagaria",
    "mpName": "Rajesh Verma",
    "authority": "District Rural Development Agency, Khagaria",
    "recommendationDate": "27 Mar 2023",
    "sanctionDate": "11 May 2024",
    "sanctionAmount": 31644000,
    "workStage": "Completed",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 30214700,
    "lastExpenditureDate": "03 Feb 2026",
    "risk": {
      "overallScore": 30,
      "level": "LOW",
      "cost": {
        "score": 30,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 43,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 10,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 35,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00107",
    "workName": "Construction of School Boundary Wall, Colony 19",
    "description": "Construction of School Boundary Wall, Colony 19 under MPLADS scheme, recommended by Rajesh Verma, MP for Khagaria.",
    "category": "Education",
    "state": "Bihar",
    "constituency": "Khagaria",
    "mpName": "Rajesh Verma",
    "authority": "Municipal Corporation Khagaria",
    "recommendationDate": "09 Jul 2022",
    "sanctionDate": "16 Nov 2023",
    "sanctionAmount": 20640000,
    "workStage": "Delayed",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 7997400,
    "lastExpenditureDate": "16 Oct 2026",
    "risk": {
      "overallScore": 55,
      "level": "MEDIUM",
      "cost": {
        "score": 76,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 90,
        "flagged": true,
        "reason": "Project has remained in the 'Delayed' stage for more than 240 days without progress update."
      },
      "expenditure": {
        "score": 13,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 19,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00108",
    "workName": "Upgradation of Primary Health Centre, Block 16",
    "description": "Upgradation of Primary Health Centre, Block 16 under MPLADS scheme, recommended by Jyotsna Charandas Mahant, MP for Korba.",
    "category": "Health",
    "state": "Chhattisgarh",
    "constituency": "Korba",
    "mpName": "Jyotsna Charandas Mahant",
    "authority": "Zila Parishad Korba",
    "recommendationDate": "03 Nov 2023",
    "sanctionDate": "07 Aug 2022",
    "sanctionAmount": 33408000,
    "workStage": "Work in Progress",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 19532800,
    "lastExpenditureDate": "16 Dec 2025",
    "risk": {
      "overallScore": 26,
      "level": "LOW",
      "cost": {
        "score": 13,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 20,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 42,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 35,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00109",
    "workName": "Construction of Overhead Water Tank, Ward No. 8",
    "description": "Construction of Overhead Water Tank, Ward No. 8 under MPLADS scheme, recommended by Jyotsna Charandas Mahant, MP for Korba.",
    "category": "Water Supply",
    "state": "Chhattisgarh",
    "constituency": "Korba",
    "mpName": "Jyotsna Charandas Mahant",
    "authority": "Zila Parishad Korba",
    "recommendationDate": "01 Nov 2021",
    "sanctionDate": "16 Jun 2022",
    "sanctionAmount": 15534000,
    "workStage": "Delayed",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 6561500,
    "lastExpenditureDate": "06 Aug 2026",
    "risk": {
      "overallScore": 56,
      "level": "MEDIUM",
      "cost": {
        "score": 45,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 81,
        "flagged": true,
        "reason": "Project has remained in the 'Delayed' stage for more than 185 days without progress update."
      },
      "expenditure": {
        "score": 34,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 68,
        "flagged": true,
        "reason": "A similar work description was found in Panchayat 21, Chhattisgarh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00110",
    "workName": "Upgradation of Primary Health Centre, Gram 14",
    "description": "Upgradation of Primary Health Centre, Gram 14 under MPLADS scheme, recommended by Malvika Devi, MP for Kalahandi.",
    "category": "Health",
    "state": "Odisha",
    "constituency": "Kalahandi",
    "mpName": "Malvika Devi",
    "authority": "District Panchayat Kalahandi",
    "recommendationDate": "20 May 2021",
    "sanctionDate": "23 Dec 2023",
    "sanctionAmount": 28957000,
    "workStage": "Delayed",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 13908100,
    "lastExpenditureDate": "14 May 2026",
    "risk": {
      "overallScore": 61,
      "level": "MEDIUM",
      "cost": {
        "score": 39,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 90,
        "flagged": true,
        "reason": "Project has remained in the 'Delayed' stage for more than 310 days without progress update."
      },
      "expenditure": {
        "score": 88,
        "flagged": true,
        "reason": "Expenditure of ₹13,908,100 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 20,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00111",
    "workName": "Improvement of Storm Water Drain, Block 9",
    "description": "Improvement of Storm Water Drain, Block 9 under MPLADS scheme, recommended by Malvika Devi, MP for Kalahandi.",
    "category": "Drainage",
    "state": "Odisha",
    "constituency": "Kalahandi",
    "mpName": "Malvika Devi",
    "authority": "Zila Parishad Kalahandi",
    "recommendationDate": "13 Oct 2021",
    "sanctionDate": "22 Jun 2024",
    "sanctionAmount": 23190000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 15109900,
    "lastExpenditureDate": "01 Dec 2024",
    "risk": {
      "overallScore": 35,
      "level": "LOW",
      "cost": {
        "score": 26,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 35,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 47,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 38,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00112",
    "workName": "Construction of Community Toilet Complex, Colony 10",
    "description": "Construction of Community Toilet Complex, Colony 10 under MPLADS scheme, recommended by Bapi Haldar, MP for Mathurapur(Sc).",
    "category": "Sanitation",
    "state": "West Bengal",
    "constituency": "Mathurapur(Sc)",
    "mpName": "Bapi Haldar",
    "authority": "Block Development Office, Mathurapur(Sc)",
    "recommendationDate": "11 Nov 2021",
    "sanctionDate": "08 Feb 2024",
    "sanctionAmount": 28358000,
    "workStage": "Completed",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 26676100,
    "lastExpenditureDate": "24 Apr 2025",
    "risk": {
      "overallScore": 28,
      "level": "LOW",
      "cost": {
        "score": 31,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 47,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 17,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 6,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00113",
    "workName": "Renovation of Panchayat Bhawan, Colony 10",
    "description": "Renovation of Panchayat Bhawan, Colony 10 under MPLADS scheme, recommended by Bapi Haldar, MP for Mathurapur(Sc).",
    "category": "Community Infrastructure",
    "state": "West Bengal",
    "constituency": "Mathurapur(Sc)",
    "mpName": "Bapi Haldar",
    "authority": "Zila Parishad Mathurapur(Sc)",
    "recommendationDate": "11 Mar 2022",
    "sanctionDate": "25 Mar 2024",
    "sanctionAmount": 7022000,
    "workStage": "Completed",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 6780100,
    "lastExpenditureDate": "11 Aug 2024",
    "risk": {
      "overallScore": 59,
      "level": "MEDIUM",
      "cost": {
        "score": 92,
        "flagged": true,
        "reason": "The sanctioned amount is 1.5x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 38,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 75,
        "flagged": true,
        "reason": "Expenditure of ₹6,780,100 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 12,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00114",
    "workName": "Renovation of Panchayat Bhawan, Gram 14",
    "description": "Renovation of Panchayat Bhawan, Gram 14 under MPLADS scheme, recommended by Bapi Haldar, MP for Mathurapur(Sc).",
    "category": "Community Infrastructure",
    "state": "West Bengal",
    "constituency": "Mathurapur(Sc)",
    "mpName": "Bapi Haldar",
    "authority": "Block Development Office, Mathurapur(Sc)",
    "recommendationDate": "01 Apr 2023",
    "sanctionDate": "21 Jan 2024",
    "sanctionAmount": 13722000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 11742300,
    "lastExpenditureDate": "08 Apr 2026",
    "risk": {
      "overallScore": 47,
      "level": "MEDIUM",
      "cost": {
        "score": 18,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 84,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 67,
        "flagged": true,
        "reason": "Expenditure of ₹11,742,300 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 20,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00115",
    "workName": "Renovation of Panchayat Bhawan, Gram 5",
    "description": "Renovation of Panchayat Bhawan, Gram 5 under MPLADS scheme, recommended by Ganesh Singh, MP for Satna.",
    "category": "Community Infrastructure",
    "state": "Madhya Pradesh",
    "constituency": "Satna",
    "mpName": "Ganesh Singh",
    "authority": "District Panchayat Satna",
    "recommendationDate": "05 Dec 2021",
    "sanctionDate": "01 Dec 2022",
    "sanctionAmount": 32244000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Om Construction Co.",
    "totalDisbursed": 29581100,
    "lastExpenditureDate": "06 Sep 2026",
    "risk": {
      "overallScore": 54,
      "level": "MEDIUM",
      "cost": {
        "score": 97,
        "flagged": true,
        "reason": "The sanctioned amount is 1.4x higher than similar community infrastructure projects in the same district."
      },
      "delay": {
        "score": 68,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 310 days without progress update."
      },
      "expenditure": {
        "score": 16,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 3,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00116",
    "workName": "Village Street Light Improvement, Sector 4",
    "description": "Village Street Light Improvement, Sector 4 under MPLADS scheme, recommended by Ganesh Singh, MP for Satna.",
    "category": "Others",
    "state": "Madhya Pradesh",
    "constituency": "Satna",
    "mpName": "Ganesh Singh",
    "authority": "District Rural Development Agency, Satna",
    "recommendationDate": "20 May 2023",
    "sanctionDate": "05 Dec 2024",
    "sanctionAmount": 10668000,
    "workStage": "Completed",
    "vendorName": "M/s Vishwakarma Contractors",
    "totalDisbursed": 10173700,
    "lastExpenditureDate": "17 Feb 2025",
    "risk": {
      "overallScore": 44,
      "level": "MEDIUM",
      "cost": {
        "score": 75,
        "flagged": true,
        "reason": "The sanctioned amount is 2.1x higher than similar others projects in the same district."
      },
      "delay": {
        "score": 41,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 26,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 14,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00117",
    "workName": "Repair of Village Road near Colony 16",
    "description": "Repair of Village Road near Colony 16 under MPLADS scheme, recommended by Eswarasamy K, MP for Pollachi.",
    "category": "Roads & Bridges",
    "state": "Tamil Nadu",
    "constituency": "Pollachi",
    "mpName": "Eswarasamy K",
    "authority": "District Panchayat Pollachi",
    "recommendationDate": "03 Mar 2022",
    "sanctionDate": "24 Feb 2024",
    "sanctionAmount": 27106000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 17108000,
    "lastExpenditureDate": "09 Feb 2026",
    "risk": {
      "overallScore": 41,
      "level": "MEDIUM",
      "cost": {
        "score": 28,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 76,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 185 days without progress update."
      },
      "expenditure": {
        "score": 33,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 22,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00118",
    "workName": "Repair of Village Road near Ward No. 5",
    "description": "Repair of Village Road near Ward No. 5 under MPLADS scheme, recommended by Eswarasamy K, MP for Pollachi.",
    "category": "Roads & Bridges",
    "state": "Tamil Nadu",
    "constituency": "Pollachi",
    "mpName": "Eswarasamy K",
    "authority": "District Rural Development Agency, Pollachi",
    "recommendationDate": "13 Jul 2021",
    "sanctionDate": "27 May 2023",
    "sanctionAmount": 14315000,
    "workStage": "Completed",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 13596500,
    "lastExpenditureDate": "28 Dec 2025",
    "risk": {
      "overallScore": 37,
      "level": "LOW",
      "cost": {
        "score": 20,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 13,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 95,
        "flagged": true,
        "reason": "Expenditure of ₹13,596,500 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 30,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00119",
    "workName": "Repair of Village Road near Gram 24",
    "description": "Repair of Village Road near Gram 24 under MPLADS scheme, recommended by Smita Uday Wagh, MP for Jalgaon.",
    "category": "Roads & Bridges",
    "state": "Maharashtra",
    "constituency": "Jalgaon",
    "mpName": "Smita Uday Wagh",
    "authority": "District Panchayat Jalgaon",
    "recommendationDate": "25 Sep 2023",
    "sanctionDate": "24 Oct 2024",
    "sanctionAmount": 19568000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 12174600,
    "lastExpenditureDate": "22 Apr 2026",
    "risk": {
      "overallScore": 46,
      "level": "MEDIUM",
      "cost": {
        "score": 49,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 25,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 34,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 90,
        "flagged": true,
        "reason": "A similar work description was found in Colony 2, Maharashtra, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00120",
    "workName": "Renovation of Primary School Building, Colony 16",
    "description": "Renovation of Primary School Building, Colony 16 under MPLADS scheme, recommended by Smita Uday Wagh, MP for Jalgaon.",
    "category": "Education",
    "state": "Maharashtra",
    "constituency": "Jalgaon",
    "mpName": "Smita Uday Wagh",
    "authority": "Block Development Office, Jalgaon",
    "recommendationDate": "13 Jul 2023",
    "sanctionDate": "15 Feb 2022",
    "sanctionAmount": 25425000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 1875000,
    "lastExpenditureDate": "15 Oct 2025",
    "risk": {
      "overallScore": 60,
      "level": "MEDIUM",
      "cost": {
        "score": 82,
        "flagged": true,
        "reason": "The sanctioned amount is 1.5x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 66,
        "flagged": true,
        "reason": "Project has remained in the 'Sanctioned' stage for more than 185 days without progress update."
      },
      "expenditure": {
        "score": 67,
        "flagged": true,
        "reason": "Expenditure of ₹1,875,000 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 2,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00121",
    "workName": "Installation of Bore Well and Hand Pump, Gram 22",
    "description": "Installation of Bore Well and Hand Pump, Gram 22 under MPLADS scheme, recommended by Ravindra Vasantrao Chavan, MP for Nanded.",
    "category": "Water Supply",
    "state": "Maharashtra",
    "constituency": "Nanded",
    "mpName": "Ravindra Vasantrao Chavan",
    "authority": "District Rural Development Agency, Nanded",
    "recommendationDate": "22 Dec 2022",
    "sanctionDate": "15 Dec 2023",
    "sanctionAmount": 31099000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 10894400,
    "lastExpenditureDate": "25 Feb 2024",
    "risk": {
      "overallScore": 50,
      "level": "MEDIUM",
      "cost": {
        "score": 83,
        "flagged": true,
        "reason": "The sanctioned amount is 2.1x higher than similar water supply projects in the same district."
      },
      "delay": {
        "score": 28,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 16,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 65,
        "flagged": true,
        "reason": "A similar work description was found in Sector 5, Maharashtra, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00122",
    "workName": "Upgradation of Primary Health Centre, Colony 7",
    "description": "Upgradation of Primary Health Centre, Colony 7 under MPLADS scheme, recommended by Ravindra Vasantrao Chavan, MP for Nanded.",
    "category": "Health",
    "state": "Maharashtra",
    "constituency": "Nanded",
    "mpName": "Ravindra Vasantrao Chavan",
    "authority": "Block Development Office, Nanded",
    "recommendationDate": "27 Nov 2021",
    "sanctionDate": "04 Oct 2024",
    "sanctionAmount": 8174000,
    "workStage": "Completed",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 7741100,
    "lastExpenditureDate": "22 Aug 2025",
    "risk": {
      "overallScore": 34,
      "level": "LOW",
      "cost": {
        "score": 41,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 13,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 47,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 34,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00123",
    "workName": "Improvement of Storm Water Drain, Sector 22",
    "description": "Improvement of Storm Water Drain, Sector 22 under MPLADS scheme, recommended by Manickam Tagore B, MP for Virudhunagar.",
    "category": "Drainage",
    "state": "Tamil Nadu",
    "constituency": "Virudhunagar",
    "mpName": "Manickam Tagore B",
    "authority": "Zila Parishad Virudhunagar",
    "recommendationDate": "26 Aug 2022",
    "sanctionDate": "14 Mar 2022",
    "sanctionAmount": 19948000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s United Builders & Co.",
    "totalDisbursed": 17291500,
    "lastExpenditureDate": "24 Dec 2026",
    "risk": {
      "overallScore": 47,
      "level": "MEDIUM",
      "cost": {
        "score": 45,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 45,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 83,
        "flagged": true,
        "reason": "Expenditure of ₹17,291,500 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 10,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00124",
    "workName": "Solid Waste Management Unit, Gram 4",
    "description": "Solid Waste Management Unit, Gram 4 under MPLADS scheme, recommended by Manickam Tagore B, MP for Virudhunagar.",
    "category": "Sanitation",
    "state": "Tamil Nadu",
    "constituency": "Virudhunagar",
    "mpName": "Manickam Tagore B",
    "authority": "District Rural Development Agency, Virudhunagar",
    "recommendationDate": "17 Jan 2022",
    "sanctionDate": "13 Jan 2022",
    "sanctionAmount": 18497000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 15463200,
    "lastExpenditureDate": "22 Jan 2024",
    "risk": {
      "overallScore": 75,
      "level": "HIGH",
      "cost": {
        "score": 97,
        "flagged": true,
        "reason": "The sanctioned amount is 1.5x higher than similar sanitation projects in the same district."
      },
      "delay": {
        "score": 81,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 28,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 89,
        "flagged": true,
        "reason": "A similar work description was found in Ward No. 12, Tamil Nadu, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00125",
    "workName": "Construction of Village Haat/Market Shed, Panchayat 17",
    "description": "Construction of Village Haat/Market Shed, Panchayat 17 under MPLADS scheme, recommended by Kali Charan Munda, MP for Khunti(St).",
    "category": "Community Infrastructure",
    "state": "Jharkhand",
    "constituency": "Khunti(St)",
    "mpName": "Kali Charan Munda",
    "authority": "Zila Parishad Khunti(St)",
    "recommendationDate": "01 Jan 2023",
    "sanctionDate": "07 May 2024",
    "sanctionAmount": 14538000,
    "workStage": "Completed",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 14509900,
    "lastExpenditureDate": "27 Aug 2026",
    "risk": {
      "overallScore": 42,
      "level": "MEDIUM",
      "cost": {
        "score": 33,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 44,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 77,
        "flagged": true,
        "reason": "Expenditure of ₹14,509,900 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 13,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00126",
    "workName": "Improvement of Storm Water Drain, Sector 2",
    "description": "Improvement of Storm Water Drain, Sector 2 under MPLADS scheme, recommended by Kali Charan Munda, MP for Khunti(St).",
    "category": "Drainage",
    "state": "Jharkhand",
    "constituency": "Khunti(St)",
    "mpName": "Kali Charan Munda",
    "authority": "Block Development Office, Khunti(St)",
    "recommendationDate": "11 Mar 2021",
    "sanctionDate": "25 Jan 2024",
    "sanctionAmount": 12908000,
    "workStage": "Work in Progress",
    "vendorName": "M/s United Builders & Co.",
    "totalDisbursed": 8141200,
    "lastExpenditureDate": "27 Oct 2026",
    "risk": {
      "overallScore": 29,
      "level": "LOW",
      "cost": {
        "score": 46,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 14,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 21,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 34,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00127",
    "workName": "Construction of Drainage System, Block 8",
    "description": "Construction of Drainage System, Block 8 under MPLADS scheme, recommended by Pralhad Venkatesh Joshi, MP for Dharwad.",
    "category": "Drainage",
    "state": "Karnataka",
    "constituency": "Dharwad",
    "mpName": "Pralhad Venkatesh Joshi",
    "authority": "District Panchayat Dharwad",
    "recommendationDate": "04 Jan 2023",
    "sanctionDate": "15 Jun 2024",
    "sanctionAmount": 23927000,
    "workStage": "Work in Progress",
    "vendorName": "M/s United Builders & Co.",
    "totalDisbursed": 16213900,
    "lastExpenditureDate": "20 Nov 2024",
    "risk": {
      "overallScore": 42,
      "level": "MEDIUM",
      "cost": {
        "score": 73,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar drainage projects in the same district."
      },
      "delay": {
        "score": 30,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 17,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 36,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00128",
    "workName": "Solid Waste Management Unit, Colony 17",
    "description": "Solid Waste Management Unit, Colony 17 under MPLADS scheme, recommended by Pralhad Venkatesh Joshi, MP for Dharwad.",
    "category": "Sanitation",
    "state": "Karnataka",
    "constituency": "Dharwad",
    "mpName": "Pralhad Venkatesh Joshi",
    "authority": "District Panchayat Dharwad",
    "recommendationDate": "01 Sep 2023",
    "sanctionDate": "07 Feb 2024",
    "sanctionAmount": 16339000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sharma Construction",
    "totalDisbursed": 6439900,
    "lastExpenditureDate": "25 Nov 2026",
    "risk": {
      "overallScore": 33,
      "level": "LOW",
      "cost": {
        "score": 16,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 37,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 19,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 76,
        "flagged": true,
        "reason": "A similar work description was found in Ward No. 3, Karnataka, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00129",
    "workName": "Construction of Additional Classroom, Govt School Block 18",
    "description": "Construction of Additional Classroom, Govt School Block 18 under MPLADS scheme, recommended by Pralhad Venkatesh Joshi, MP for Dharwad.",
    "category": "Education",
    "state": "Karnataka",
    "constituency": "Dharwad",
    "mpName": "Pralhad Venkatesh Joshi",
    "authority": "District Rural Development Agency, Dharwad",
    "recommendationDate": "18 Feb 2023",
    "sanctionDate": "24 Nov 2022",
    "sanctionAmount": 15769000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Sarvodaya Construction",
    "totalDisbursed": 6695700,
    "lastExpenditureDate": "25 Feb 2026",
    "risk": {
      "overallScore": 53,
      "level": "MEDIUM",
      "cost": {
        "score": 99,
        "flagged": true,
        "reason": "The sanctioned amount is 1.5x higher than similar education projects in the same district."
      },
      "delay": {
        "score": 42,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 29,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 20,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00130",
    "workName": "Installation of Solar Street Lights, Panchayat 18",
    "description": "Installation of Solar Street Lights, Panchayat 18 under MPLADS scheme, recommended by Atul Garg, MP for Ghaziabad.",
    "category": "Others",
    "state": "Uttar Pradesh",
    "constituency": "Ghaziabad",
    "mpName": "Atul Garg",
    "authority": "Zila Parishad Ghaziabad",
    "recommendationDate": "12 Nov 2023",
    "sanctionDate": "28 Sep 2022",
    "sanctionAmount": 11368000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Bharat Infra Works",
    "totalDisbursed": 10641000,
    "lastExpenditureDate": "04 Mar 2026",
    "risk": {
      "overallScore": 80,
      "level": "HIGH",
      "cost": {
        "score": 84,
        "flagged": true,
        "reason": "The sanctioned amount is 1.9x higher than similar others projects in the same district."
      },
      "delay": {
        "score": 87,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 210 days without progress update."
      },
      "expenditure": {
        "score": 74,
        "flagged": true,
        "reason": "Expenditure of ₹10,641,000 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 69,
        "flagged": true,
        "reason": "A similar work description was found in Colony 9, Uttar Pradesh, sanctioned within the same recommendation cycle."
      }
    }
  },
  {
    "projectId": "MPLADS-00131",
    "workName": "Construction of CC Road at Colony 15",
    "description": "Construction of CC Road at Colony 15 under MPLADS scheme, recommended by Kani K Navas, MP for Ramanathapuram.",
    "category": "Roads & Bridges",
    "state": "Tamil Nadu",
    "constituency": "Ramanathapuram",
    "mpName": "Kani K Navas",
    "authority": "Zila Parishad Ramanathapuram",
    "recommendationDate": "04 Apr 2023",
    "sanctionDate": "03 Oct 2023",
    "sanctionAmount": 14613000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 215300,
    "lastExpenditureDate": "16 Jun 2024",
    "risk": {
      "overallScore": 23,
      "level": "LOW",
      "cost": {
        "score": 29,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 19,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 30,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 12,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00132",
    "workName": "Drinking Water Supply Scheme, Gram 24",
    "description": "Drinking Water Supply Scheme, Gram 24 under MPLADS scheme, recommended by Kani K Navas, MP for Ramanathapuram.",
    "category": "Water Supply",
    "state": "Tamil Nadu",
    "constituency": "Ramanathapuram",
    "mpName": "Kani K Navas",
    "authority": "District Rural Development Agency, Ramanathapuram",
    "recommendationDate": "18 Aug 2022",
    "sanctionDate": "21 Mar 2022",
    "sanctionAmount": 16435000,
    "workStage": "Completed",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 15728800,
    "lastExpenditureDate": "27 Feb 2026",
    "risk": {
      "overallScore": 31,
      "level": "LOW",
      "cost": {
        "score": 44,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 50,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 11,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 3,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00133",
    "workName": "Widening of Approach Road, Colony 9",
    "description": "Widening of Approach Road, Colony 9 under MPLADS scheme, recommended by Pathan Yusuf, MP for Baharampur.",
    "category": "Roads & Bridges",
    "state": "West Bengal",
    "constituency": "Baharampur",
    "mpName": "Pathan Yusuf",
    "authority": "District Rural Development Agency, Baharampur",
    "recommendationDate": "03 Sep 2023",
    "sanctionDate": "17 Jun 2023",
    "sanctionAmount": 23691000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Ganga Infrastructure Pvt. Ltd.",
    "totalDisbursed": 15426300,
    "lastExpenditureDate": "08 Nov 2024",
    "risk": {
      "overallScore": 39,
      "level": "LOW",
      "cost": {
        "score": 49,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 42,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 21,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 38,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00134",
    "workName": "Repair of Village Road near Panchayat 16",
    "description": "Repair of Village Road near Panchayat 16 under MPLADS scheme, recommended by Pathan Yusuf, MP for Baharampur.",
    "category": "Roads & Bridges",
    "state": "West Bengal",
    "constituency": "Baharampur",
    "mpName": "Pathan Yusuf",
    "authority": "District Rural Development Agency, Baharampur",
    "recommendationDate": "02 Jan 2022",
    "sanctionDate": "04 Jun 2024",
    "sanctionAmount": 7483000,
    "workStage": "Work in Progress",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 2567000,
    "lastExpenditureDate": "21 Sep 2026",
    "risk": {
      "overallScore": 30,
      "level": "LOW",
      "cost": {
        "score": 26,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 46,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 34,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 6,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00135",
    "workName": "Solid Waste Management Unit, Block 16",
    "description": "Solid Waste Management Unit, Block 16 under MPLADS scheme, recommended by Santosh Pandey, MP for Rajnandgaon.",
    "category": "Sanitation",
    "state": "Chhattisgarh",
    "constituency": "Rajnandgaon",
    "mpName": "Santosh Pandey",
    "authority": "District Panchayat Rajnandgaon",
    "recommendationDate": "06 Mar 2021",
    "sanctionDate": "23 Oct 2023",
    "sanctionAmount": 29520000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 3905600,
    "lastExpenditureDate": "08 Nov 2024",
    "risk": {
      "overallScore": 39,
      "level": "LOW",
      "cost": {
        "score": 17,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 40,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 75,
        "flagged": true,
        "reason": "Expenditure of ₹3,905,600 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 28,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00136",
    "workName": "Construction of School Boundary Wall, Panchayat 21",
    "description": "Construction of School Boundary Wall, Panchayat 21 under MPLADS scheme, recommended by Santosh Pandey, MP for Rajnandgaon.",
    "category": "Education",
    "state": "Chhattisgarh",
    "constituency": "Rajnandgaon",
    "mpName": "Santosh Pandey",
    "authority": "Municipal Corporation Rajnandgaon",
    "recommendationDate": "01 Nov 2023",
    "sanctionDate": "22 Dec 2024",
    "sanctionAmount": 6657000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 4413700,
    "lastExpenditureDate": "07 Feb 2025",
    "risk": {
      "overallScore": 37,
      "level": "LOW",
      "cost": {
        "score": 40,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 48,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 21,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 34,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00137",
    "workName": "Improvement of Storm Water Drain, Panchayat 13",
    "description": "Improvement of Storm Water Drain, Panchayat 13 under MPLADS scheme, recommended by Santosh Pandey, MP for Rajnandgaon.",
    "category": "Drainage",
    "state": "Chhattisgarh",
    "constituency": "Rajnandgaon",
    "mpName": "Santosh Pandey",
    "authority": "District Rural Development Agency, Rajnandgaon",
    "recommendationDate": "20 Aug 2021",
    "sanctionDate": "26 Jan 2024",
    "sanctionAmount": 8032000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 629800,
    "lastExpenditureDate": "25 Sep 2026",
    "risk": {
      "overallScore": 68,
      "level": "MEDIUM",
      "cost": {
        "score": 76,
        "flagged": true,
        "reason": "The sanctioned amount is 2.2x higher than similar drainage projects in the same district."
      },
      "delay": {
        "score": 65,
        "flagged": true,
        "reason": "Project has remained in the 'Sanctioned' stage for more than 270 days without progress update."
      },
      "expenditure": {
        "score": 88,
        "flagged": true,
        "reason": "Expenditure of ₹629,800 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 35,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00138",
    "workName": "Construction of Community Toilet Complex, Colony 24",
    "description": "Construction of Community Toilet Complex, Colony 24 under MPLADS scheme, recommended by Malvinder Singh Kang, MP for Anandpur Sahib.",
    "category": "Sanitation",
    "state": "Punjab",
    "constituency": "Anandpur Sahib",
    "mpName": "Malvinder Singh Kang",
    "authority": "District Rural Development Agency, Anandpur Sahib",
    "recommendationDate": "01 Apr 2022",
    "sanctionDate": "26 Dec 2024",
    "sanctionAmount": 17983000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 11860500,
    "lastExpenditureDate": "17 Oct 2024",
    "risk": {
      "overallScore": 64,
      "level": "MEDIUM",
      "cost": {
        "score": 92,
        "flagged": true,
        "reason": "The sanctioned amount is 1.6x higher than similar sanitation projects in the same district."
      },
      "delay": {
        "score": 36,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 92,
        "flagged": true,
        "reason": "Expenditure of ₹11,860,500 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 18,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00139",
    "workName": "Solid Waste Management Unit, Colony 9",
    "description": "Solid Waste Management Unit, Colony 9 under MPLADS scheme, recommended by Malvinder Singh Kang, MP for Anandpur Sahib.",
    "category": "Sanitation",
    "state": "Punjab",
    "constituency": "Anandpur Sahib",
    "mpName": "Malvinder Singh Kang",
    "authority": "District Rural Development Agency, Anandpur Sahib",
    "recommendationDate": "12 Oct 2022",
    "sanctionDate": "24 Jul 2024",
    "sanctionAmount": 23010000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 16787500,
    "lastExpenditureDate": "04 Nov 2024",
    "risk": {
      "overallScore": 33,
      "level": "LOW",
      "cost": {
        "score": 20,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 86,
        "flagged": true,
        "reason": "Project has remained in the 'Physical Inspection' stage for more than 310 days without progress update."
      },
      "expenditure": {
        "score": 13,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 2,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00140",
    "workName": "Renovation of Panchayat Bhawan, Ward No. 3",
    "description": "Renovation of Panchayat Bhawan, Ward No. 3 under MPLADS scheme, recommended by Malvinder Singh Kang, MP for Anandpur Sahib.",
    "category": "Community Infrastructure",
    "state": "Punjab",
    "constituency": "Anandpur Sahib",
    "mpName": "Malvinder Singh Kang",
    "authority": "District Panchayat Anandpur Sahib",
    "recommendationDate": "02 Oct 2023",
    "sanctionDate": "16 Nov 2022",
    "sanctionAmount": 9297000,
    "workStage": "Sanctioned",
    "vendorName": "M/s Shakti Builders",
    "totalDisbursed": 52700,
    "lastExpenditureDate": "07 Jan 2025",
    "risk": {
      "overallScore": 23,
      "level": "LOW",
      "cost": {
        "score": 43,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 12,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 24,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 4,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00141",
    "workName": "Construction of Sub-Health Centre, Sector 12",
    "description": "Construction of Sub-Health Centre, Sector 12 under MPLADS scheme, recommended by Balabhadra Majhi, MP for Nabarangpur(St).",
    "category": "Health",
    "state": "Odisha",
    "constituency": "Nabarangpur(St)",
    "mpName": "Balabhadra Majhi",
    "authority": "Block Development Office, Nabarangpur(St)",
    "recommendationDate": "12 Oct 2023",
    "sanctionDate": "08 May 2023",
    "sanctionAmount": 17531000,
    "workStage": "Work in Progress",
    "vendorName": "M/s Prime Engineering Works",
    "totalDisbursed": 9933600,
    "lastExpenditureDate": "15 Apr 2026",
    "risk": {
      "overallScore": 31,
      "level": "LOW",
      "cost": {
        "score": 26,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 42,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 42,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 9,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00142",
    "workName": "Construction of Crematorium Shed, Sector 19",
    "description": "Construction of Crematorium Shed, Sector 19 under MPLADS scheme, recommended by K Radhakrishnan, MP for Alathur(Sc).",
    "category": "Others",
    "state": "Kerala",
    "constituency": "Alathur(Sc)",
    "mpName": "K Radhakrishnan",
    "authority": "Zila Parishad Alathur(Sc)",
    "recommendationDate": "03 May 2021",
    "sanctionDate": "26 Nov 2023",
    "sanctionAmount": 26591000,
    "workStage": "Completed",
    "vendorName": "M/s Metro Civil Works",
    "totalDisbursed": 25712100,
    "lastExpenditureDate": "23 Nov 2024",
    "risk": {
      "overallScore": 33,
      "level": "LOW",
      "cost": {
        "score": 32,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 10,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 70,
        "flagged": true,
        "reason": "Expenditure of ₹25,712,100 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 23,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00143",
    "workName": "Solid Waste Management Unit, Block 7",
    "description": "Solid Waste Management Unit, Block 7 under MPLADS scheme, recommended by K Radhakrishnan, MP for Alathur(Sc).",
    "category": "Sanitation",
    "state": "Kerala",
    "constituency": "Alathur(Sc)",
    "mpName": "K Radhakrishnan",
    "authority": "District Rural Development Agency, Alathur(Sc)",
    "recommendationDate": "08 Apr 2022",
    "sanctionDate": "27 Apr 2022",
    "sanctionAmount": 9762000,
    "workStage": "Completed",
    "vendorName": "M/s Rajdhani Infra Projects",
    "totalDisbursed": 9164500,
    "lastExpenditureDate": "05 Jun 2026",
    "risk": {
      "overallScore": 55,
      "level": "MEDIUM",
      "cost": {
        "score": 74,
        "flagged": true,
        "reason": "The sanctioned amount is 2.0x higher than similar sanitation projects in the same district."
      },
      "delay": {
        "score": 41,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 67,
        "flagged": true,
        "reason": "Expenditure of ₹9,164,500 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 25,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00144",
    "workName": "Construction of Crematorium Shed, Panchayat 17",
    "description": "Construction of Crematorium Shed, Panchayat 17 under MPLADS scheme, recommended by Patel Umeshbhai Babubhai, MP for Daman And Diu.",
    "category": "Others",
    "state": "The Dadra And Nagar Haveli And Daman And Diu",
    "constituency": "Daman And Diu",
    "mpName": "Patel Umeshbhai Babubhai",
    "authority": "Municipal Corporation Daman And Diu",
    "recommendationDate": "28 Jul 2022",
    "sanctionDate": "15 Mar 2024",
    "sanctionAmount": 28829000,
    "workStage": "Completed",
    "vendorName": "M/s National Engineering Co.",
    "totalDisbursed": 28689800,
    "lastExpenditureDate": "17 Dec 2024",
    "risk": {
      "overallScore": 36,
      "level": "LOW",
      "cost": {
        "score": 10,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 34,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 88,
        "flagged": true,
        "reason": "Expenditure of ₹28,689,800 is unusually high compared to the physical progress reported for this work."
      },
      "duplicate": {
        "score": 18,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  },
  {
    "projectId": "MPLADS-00145",
    "workName": "Construction of Sub-Health Centre, Sector 20",
    "description": "Construction of Sub-Health Centre, Sector 20 under MPLADS scheme, recommended by Patel Umeshbhai Babubhai, MP for Daman And Diu.",
    "category": "Health",
    "state": "The Dadra And Nagar Haveli And Daman And Diu",
    "constituency": "Daman And Diu",
    "mpName": "Patel Umeshbhai Babubhai",
    "authority": "Block Development Office, Daman And Diu",
    "recommendationDate": "05 Oct 2021",
    "sanctionDate": "08 Nov 2024",
    "sanctionAmount": 24263000,
    "workStage": "Physical Inspection",
    "vendorName": "M/s Kisan Infra Developers",
    "totalDisbursed": 17719500,
    "lastExpenditureDate": "09 Dec 2024",
    "risk": {
      "overallScore": 23,
      "level": "LOW",
      "cost": {
        "score": 34,
        "flagged": false,
        "reason": "Sanctioned amount is within the expected range for similar works in the district."
      },
      "delay": {
        "score": 19,
        "flagged": false,
        "reason": "Project timeline is broadly consistent with the sanctioned schedule."
      },
      "expenditure": {
        "score": 21,
        "flagged": false,
        "reason": "Reported expenditure is proportionate to physical progress."
      },
      "duplicate": {
        "score": 10,
        "flagged": false,
        "reason": "No similar or duplicate work descriptions were found nearby."
      }
    }
  }
];
