package io.continuum.knit
import java.io.File
import scopt._

case class ClientConfig(numContainers: Int = 1, memory: Int = 300, virtualCores: Int = 1,
                  command: String = "", pythonEnv: String = "", debug: Boolean = false)

object ClientArguments {
  val parser = new scopt.OptionParser[ClientConfig]("scopt") {
    head("knit", "x.1")
    opt[Int]('n', "numContainers") action { (x, c) =>
      c.copy(numContainers = x)
    } text ("Number of YARN containers")

    opt[Int]('m', "memory") action { (x, c) =>
      c.copy(memory = x)
    } text ("Amount of memory per container")

    opt[Int]('c', "virtualCores") action { (x, c) =>
      c.copy(virtualCores = x)
    } text ("Virtual cores per container")

    opt[String]('C', "command") action { (x, c) =>
      c.copy(command = x)
    } text ("Command to run in containers")

    opt[String]('p', "pythonEnv") action { (x, c) =>
      c.copy(pythonEnv = x)
    } text ("Number of YARN containers ")

    opt[Unit]("debug") hidden() action { (_, c) =>
      c.copy(debug = true)
    } text ("this option is hidden in the usage text")

    help("help") text ("command line for launching distributed python")

  }

  def parseArgs(args: Array[String]) : ClientConfig = {
    val parsed = parser.parse(args, ClientConfig())
    val parsedArgs = parsed.getOrElse( sys.exit(1) )
    parsedArgs
  }

  def ApplicationMasterCMD(config: ClientConfig): String = {

    var cmdSeq = Seq.empty[String]

    //generate list of tuples from Config CLI parser
    val fields = (Map[String, Any]() /: config.getClass.getDeclaredFields) { (a, f) =>
      f.setAccessible(true)
      a + (f.getName -> f.get(config))
    }

    fields.foreach { case (k, v) =>
      v match {
        case v: Boolean =>
          if (v)
            cmdSeq = cmdSeq :+ s" --$k $v "
        case v: List[_] =>
          if (!v.isEmpty)
            cmdSeq = cmdSeq :+ s" --$k $v "
        case v: Map[_, _] =>
          if (!v.isEmpty)
            cmdSeq = cmdSeq :+ s" --$k $v "
        case v: Seq[_] =>
          if (!v.isEmpty)
            cmdSeq = cmdSeq :+ s" --$k $v "
        case v: String =>
          if (!v.isEmpty)
            cmdSeq = cmdSeq :+ s" --$k $v "
        case v: Int =>
          cmdSeq = cmdSeq :+ s" --$k $v "
      }
    }
    cmdSeq.mkString(" ")
  }
}