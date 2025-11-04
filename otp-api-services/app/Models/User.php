<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class User extends Authenticatable
{
    use HasFactory, Notifiable;

    protected $fillable = [
        'name', 'email', 'password', 'points'
    ];

    protected $hidden = [
        'password', 'remember_token',
    ];

    // Relationships
    public function numberAssignments()
    {
        return $this->hasMany(NumberAssignment::class);
    }

    public function smsMessages()
    {
        return $this->hasMany(SMSMessage::class);
    }

    public function pointsHistory()
    {
        return $this->hasMany(UserPoint::class);
    }

    public function withdrawals()
    {
        return $this->hasMany(Withdrawal::class);
    }
}
