<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class SMSMessage extends Model
{
    use HasFactory;

    protected $fillable = [
        'number_id', 'user_id', 'sender_number', 'message', 'received_at'
    ];

    protected $dates = ['received_at', 'created_at', 'updated_at'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function number()
    {
        return $this->belongsTo(Number::class);
    }
}
