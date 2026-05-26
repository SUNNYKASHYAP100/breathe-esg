"""
Multi-tenant models for Breathe ESG
"""
from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    """Represents a tenant company in the system"""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.name


class CompanyUser(models.Model):
    """Links users to companies with role-based access"""
    ROLES = (
        ('admin', 'Administrator'),
        ('analyst', 'Analyst'),
        ('uploader', 'Data Uploader'),
        ('viewer', 'Viewer'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    role = models.CharField(max_length=20, choices=ROLES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('company', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name} ({self.role})"
