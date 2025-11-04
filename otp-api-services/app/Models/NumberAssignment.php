<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class NumberAssignment extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'number_id', 'assigned_at', 'expire_at', 'active'
    ];

    protected $dates = [
        'assigned_at', 'expire_at', 'created_at', 'updated_at'
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function number()
    {
        return $this->belongsTo(Number::class);
    }
}
