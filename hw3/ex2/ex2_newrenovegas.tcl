#Create a simulator object
set ns [new Simulator]
set file [lindex $argv 0]
#Open the trace file
set tf [open $file w]
$ns trace-all $tf

#Define a 'finish' procedure
proc finish {} {
        global ns tf
        $ns flush-trace
        close $tf
        exit 0
}

#Create four nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n5 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null
$udp set fid_ 2

set rate [lindex $argv 1]

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ $rate
$cbr set random_ false

set tcp [new Agent/TCP/Newreno]
$tcp set class_ 2
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1
set ftp [new Application/FTP]
$ftp attach-agent $tcp

set tcp2 [new Agent/TCP/Vegas]
$tcp2 set class_ 2
$ns attach-agent $n5 $tcp2
set sink [new Agent/TCPSink]
$ns attach-agent $n6 $sink
$ns connect $tcp2 $sink
$tcp2 set fid_ 1
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2


#Schedule events for the CBR 
$ns at 0.1 "$cbr start"
$ns at 0.1 "$ftp start"
$ns at 0.1 "$ftp2 start"
$ns at 10.1 "$cbr stop"
$ns at 10.1 "$ftp stop"
$ns at 10.1 "$ftp2 stop"

#Call the finish procedure after 5 seconds of simulation time
$ns at 10.2 "finish"

#Run the simulation
$ns run