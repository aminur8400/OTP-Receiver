<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UserDataController extends Controller
{
    public function userSms(Request $r){
        $sms = $r->user()->smsMessages()->with('number')->orderBy('received_at','desc')->paginate(50);
        return response()->json($sms);
    }

    public function points(Request $r){
        return response()->json([
            'points' => $r->user()->points,
            'history' => $r->user()->pointsHistory()->orderBy('created_at','desc')->limit(50)->get()
        ]);
    }
}
