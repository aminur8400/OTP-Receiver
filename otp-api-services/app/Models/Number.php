<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Number extends Model
{
    use HasFactory;

    protected $fillable = [
        'number', 'country', 'sid', 'paid', 'limit_status'
    ];

    public function assignments()
    {
        return $this->hasMany(NumberAssignment::class);
    }

    public function smsMessages()
    {
        return $this->hasMany(SMSMessage::class);
    }
}
